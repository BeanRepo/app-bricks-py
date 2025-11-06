# SPDX-FileCopyrightText: Copyright (C) 2025 ARDUINO SA <http://www.arduino.cc>
#
# SPDX-License-Identifier: MPL-2.0

import math
import threading
import time
import numpy as np
from typing import Literal
from arduino.app_utils import Logger, brick
from arduino.app_peripherals.speaker import Speaker

logger = Logger("WaveGenerator")


WaveType = Literal["sine", "square", "sawtooth", "triangle"]


@brick
class WaveGenerator:
    """Continuous wave generator brick for audio synthesis.

    This brick generates continuous audio waveforms (sine, square, sawtooth, triangle)
    and streams them to a USB speaker in real-time. It provides smooth transitions
    between frequency and amplitude changes using configurable envelope parameters.

    The generator runs continuously in a background thread, producing audio blocks
    at a steady rate with minimal latency.

    Attributes:
        sample_rate (int): Audio sample rate in Hz (default: 16000).
        wave_type (WaveType): Type of waveform to generate.
        frequency (float): Current output frequency in Hz.
        amplitude (float): Current output amplitude (0.0-1.0).
        master_volume (float): Global volume multiplier (0.0-1.0).
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        wave_type: WaveType = "sine",
        block_duration: float = 0.03,
        attack: float = 0.01,
        release: float = 0.03,
        glide: float = 0.02,
        speaker: Speaker = None,
    ):
        """Initialize the WaveGenerator brick.

        Args:
            sample_rate (int): Audio sample rate in Hz (default: 16000).
            wave_type (WaveType): Initial waveform type (default: "sine").
            block_duration (float): Duration of each audio block in seconds (default: 0.03).
            attack (float): Attack time for amplitude envelope in seconds (default: 0.01).
            release (float): Release time for amplitude envelope in seconds (default: 0.03).
            glide (float): Frequency glide time (portamento) in seconds (default: 0.02).
            speaker (Speaker, optional): Pre-configured Speaker instance. If None, a new Speaker
                will be created with default settings (auto-detect device, FLOAT_LE format).
                WaveGenerator will manage the speaker's lifecycle (calling start/stop).

        Raises:
            SpeakerException: If no USB speaker is found or device is busy.
        """
        self.sample_rate = int(sample_rate)
        self.block_duration = float(block_duration)
        self.wave_type = wave_type

        # Envelope parameters
        self.attack = float(attack)
        self.release = float(release)
        self.glide = float(glide)

        # Target state (updated by user)
        self._target_freq = 440.0
        self._target_amp = 0.0
        self.master_volume = 0.8

        # Current state (internal, smoothed)
        self._current_freq = 440.0
        self._current_amp = 0.0
        self._phase = 0.0

        # Pre-allocated buffers
        self._buf_N = 0
        self._buf_phase_incs = None
        self._buf_phases = None
        self._buf_envelope = None
        self._buf_samples = None

        # Speaker setup
        if speaker is not None:
            # Use externally provided Speaker instance
            self._speaker = speaker
            logger.debug("Using externally provided Speaker instance")
        else:
            # Create internal Speaker instance with default settings
            self._speaker = Speaker(
                device=None,  # Auto-detect first available USB speaker
                sample_rate=sample_rate,
                channels=1,
                format="FLOAT_LE",
            )
            logger.debug(
                "Created internal Speaker: device=auto-detect, sample_rate=%d, format=FLOAT_LE",
                sample_rate,
            )

        # Producer thread control
        self._running = threading.Event()
        self._producer_thread = None
        self._state_lock = threading.Lock()

        logger.info(
            "WaveGenerator initialized: sample_rate=%d, wave_type=%s, block_dur=%.3fs",
            sample_rate,
            wave_type,
            block_duration,
        )

    def start(self):
        """Start the wave generator and audio output.

        This starts the speaker device and launches the producer thread that
        continuously generates and streams audio blocks.
        """
        if self._running.is_set():
            logger.warning("WaveGenerator is already running")
            return

        logger.debug("Starting WaveGenerator...")
        self._speaker.start()
        self._running.set()

        self._producer_thread = threading.Thread(target=self._producer_loop, daemon=True, name="WaveGenerator-Producer")
        self._producer_thread.start()

        logger.info("WaveGenerator started")

    def stop(self):
        """Stop the wave generator and audio output.

        This stops the producer thread and closes the speaker device.
        """
        if not self._running.is_set():
            logger.warning("WaveGenerator is not running")
            return

        logger.debug("Stopping WaveGenerator...")
        self._running.clear()

        if self._producer_thread:
            self._producer_thread.join(timeout=5)
            if self._producer_thread.is_alive():
                logger.warning("Producer thread did not terminate in time")
            self._producer_thread = None

        self._speaker.stop()
        logger.info("WaveGenerator stopped")

    def set_frequency(self, frequency: float):
        """Set the target output frequency.

        The frequency will smoothly transition to the new value over the
        configured glide time.

        Args:
            frequency (float): Target frequency in Hz (typically 20-8000 Hz).
        """
        with self._state_lock:
            self._target_freq = float(max(0.0, frequency))

    def set_amplitude(self, amplitude: float):
        """Set the target output amplitude.

        The amplitude will smoothly transition to the new value over the
        configured attack/release time.

        Args:
            amplitude (float): Target amplitude in range [0.0, 1.0].
        """
        with self._state_lock:
            self._target_amp = float(max(0.0, min(1.0, amplitude)))

    def set_wave_type(self, wave_type: WaveType):
        """Change the waveform type.

        Args:
            wave_type (WaveType): One of "sine", "square", "sawtooth", "triangle".

        Raises:
            ValueError: If wave_type is not valid.
        """
        valid_types = ["sine", "square", "sawtooth", "triangle"]
        if wave_type not in valid_types:
            raise ValueError(f"Invalid wave_type '{wave_type}'. Must be one of {valid_types}")

        with self._state_lock:
            self.wave_type = wave_type
        logger.debug(f"Wave type changed to: {wave_type}")

    def set_volume(self, volume: float):
        """Set the master volume level.

        Args:
            volume (float): Master volume in range [0.0, 1.0].
        """
        with self._state_lock:
            self.master_volume = float(max(0.0, min(1.0, volume)))

    def set_envelope_params(self, attack: float = None, release: float = None, glide: float = None):
        """Update envelope parameters.

        Args:
            attack (float, optional): Attack time in seconds.
            release (float, optional): Release time in seconds.
            glide (float, optional): Frequency glide time in seconds.
        """
        with self._state_lock:
            if attack is not None:
                self.attack = float(max(0.0, attack))
            if release is not None:
                self.release = float(max(0.0, release))
            if glide is not None:
                self.glide = float(max(0.0, glide))

    def get_state(self) -> dict:
        """Get current generator state.

        Returns:
            dict: Dictionary containing current frequency, amplitude, wave type, etc.
        """
        with self._state_lock:
            return {
                "frequency": self._current_freq,
                "amplitude": self._current_amp,
                "wave_type": self.wave_type,
                "master_volume": self.master_volume,
                "phase": self._phase,
            }

    def _producer_loop(self):
        """Main producer loop running in background thread.

        Continuously generates audio blocks at a steady cadence and streams
        them to the speaker device.
        """
        next_time = time.perf_counter()

        while self._running.is_set():
            next_time += self.block_duration

            # Read target state
            with self._state_lock:
                target_freq = self._target_freq
                target_amp = self._target_amp
                wave_type = self.wave_type
                master_volume = self.master_volume

            # Generate audio block
            try:
                audio_block = self._generate_block(target_freq, target_amp, wave_type, master_volume)
                self._speaker.play(audio_block, block_on_queue=False)
            except Exception as e:
                logger.error(f"Error generating audio block: {e}")

            # Wait until next scheduled time
            now = time.perf_counter()
            sleep_time = next_time - now
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                # We're falling behind, reset timing
                next_time = now

        logger.debug("Producer loop terminated")

    def _generate_block(self, freq_target: float, amp_target: float, wave_type: str, master_volume: float) -> np.ndarray:
        """Generate a single audio block.

        Args:
            freq_target (float): Target frequency in Hz.
            amp_target (float): Target amplitude (0.0-1.0).
            wave_type (str): Waveform type.
            master_volume (float): Master volume multiplier.

        Returns:
            np.ndarray: Audio samples as float32 array.
        """
        N = max(1, int(self.sample_rate * self.block_duration))

        # Ensure buffers are allocated
        if N > self._buf_N:
            self._buf_N = N
            self._buf_phase_incs = np.empty(self._buf_N, dtype=np.float32)
            self._buf_phases = np.empty(self._buf_N, dtype=np.float32)
            self._buf_envelope = np.empty(self._buf_N, dtype=np.float32)
            self._buf_samples = np.empty(self._buf_N, dtype=np.float32)

        phases = self._buf_phases[:N]
        envelope = self._buf_envelope[:N]
        samples = self._buf_samples[:N]

        # === AMPLITUDE SMOOTHING ===
        amp_current = self._current_amp
        if amp_target == amp_current or (self.attack <= 0.0 and self.release <= 0.0):
            envelope.fill(amp_target)
        else:
            ramp = self.attack if amp_target > amp_current else self.release
            if ramp <= 0.0:
                envelope.fill(amp_target)
            else:
                frac = min(1.0, self.block_duration / ramp)
                next_amp = amp_current + (amp_target - amp_current) * frac
                envelope[:] = np.linspace(amp_current, next_amp, N, dtype=np.float32)
                amp_current = float(envelope[-1])

        # === FREQUENCY GLIDE (PORTAMENTO) ===
        freq_current = self._current_freq
        phase_incs = self._buf_phase_incs[:N]

        if self.glide > 0.0 and freq_current != freq_target:
            # Apply glide smoothing over time
            frac = min(1.0, self.block_duration / self.glide)
            next_freq = freq_current + (freq_target - freq_current) * frac

            # Linear interpolation within block
            freq_ramp = np.linspace(freq_current, next_freq, N, dtype=np.float32)
            phase_incs[:] = 2.0 * math.pi * freq_ramp / float(self.sample_rate)

            freq_current = float(next_freq)
        else:
            # No glide or already at target
            phase_incr = 2.0 * math.pi * freq_target / float(self.sample_rate)
            phase_incs.fill(phase_incr)
            freq_current = freq_target

        # === PHASE ACCUMULATION ===
        np.cumsum(phase_incs, dtype=np.float32, out=phases)
        phases += self._phase
        self._phase = float(phases[-1] % (2.0 * math.pi))

        # === WAVEFORM GENERATION ===
        if wave_type == "sine":
            np.sin(phases, out=samples)
        elif wave_type == "square":
            samples[:] = np.where(np.sin(phases) >= 0, 1.0, -1.0)
        elif wave_type == "sawtooth":
            samples[:] = 2.0 * (phases / (2.0 * math.pi) % 1.0) - 1.0
        elif wave_type == "triangle":
            samples[:] = 2.0 * np.abs(2.0 * (phases / (2.0 * math.pi) % 1.0) - 1.0) - 1.0
        else:
            # Fallback to sine
            np.sin(phases, out=samples)

        # === APPLY ENVELOPE AND GAIN ===
        np.multiply(samples, envelope, out=samples)
        if master_volume != 1.0:
            np.multiply(samples, master_volume, out=samples)

        # Update internal state
        self._current_amp = amp_current
        self._current_freq = freq_current

        return samples
