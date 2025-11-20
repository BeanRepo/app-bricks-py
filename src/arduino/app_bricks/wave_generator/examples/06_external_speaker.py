# SPDX-FileCopyrightText: Copyright (C) 2025 ARDUINO SA <http://www.arduino.cc>
#
# SPDX-License-Identifier: MPL-2.0

"""
Custom Speaker Configuration Example

Demonstrates how to use a pre-configured Speaker instance with WaveGenerator.
Use this approach when you need:
- Specific USB speaker selection (USB_SPEAKER_2, etc.)
- Different audio format (S16_LE, etc.)
- Explicit device name ("plughw:CARD=Device,DEV=0")
"""

import time
from arduino.app_bricks.wave_generator import WaveGenerator
from arduino.app_peripherals.speaker import Speaker
from arduino.app_utils import App

# List available USB speakers
available_speakers = Speaker.list_usb_devices()
print(f"Available USB speakers: {available_speakers}")

# Create and configure a Speaker with specific parameters
speaker = Speaker(
    device=Speaker.USB_SPEAKER_1,  # or None for auto-detect, or specific device
    sample_rate=16000,
    channels=1,
    format="FLOAT_LE",
)

# Create WaveGenerator with the external speaker
# WaveGenerator will manage the speaker's lifecycle (start/stop)
wave_gen = WaveGenerator(
    sample_rate=16000,
    speaker=speaker,  # Pass pre-configured speaker
    wave_type="sine",
    glide=0.02,
)

# Start the WaveGenerator (which will also start the speaker)
App.start_brick(wave_gen)


def play_sequence():
    """Play a simple frequency sequence."""
    frequencies = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]  # C4 to C5

    for freq in frequencies:
        print(f"Playing {freq:.2f} Hz")
        wave_gen.set_frequency(freq)
        wave_gen.set_amplitude(0.7)
        time.sleep(0.5)

    # Fade out
    wave_gen.set_amplitude(0.0)
    time.sleep(1)


print("Playing musical scale with external speaker...")
print("Press Ctrl+C to stop")

App.run(user_loop=play_sequence)

# WaveGenerator automatically stops the speaker when it stops
print("Done")
