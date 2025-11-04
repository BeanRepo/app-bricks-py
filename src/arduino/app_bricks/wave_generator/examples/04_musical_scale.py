# SPDX-FileCopyrightText: Copyright (C) 2025 ARDUINO SA <http://www.arduino.cc>
#
# SPDX-License-Identifier: MPL-2.0

"""
Musical Scale Example

Plays a musical scale (C major) demonstrating discrete note transitions
with smooth glide between notes.
"""

import time
from arduino.app_bricks.wave_generator import WaveGenerator
from arduino.app_utils import App

# Musical note frequencies (C major scale)
NOTES = {
    "C4": 261.63,
    "D4": 293.66,
    "E4": 329.63,
    "F4": 349.23,
    "G4": 392.00,
    "A4": 440.00,
    "B4": 493.88,
    "C5": 523.25,
}

wave_gen = WaveGenerator(
    wave_type="triangle",  # Soft triangle wave
    glide=0.03,  # 30ms glide between notes
    attack=0.01,
    release=0.05,
)

App.start_brick(wave_gen)
wave_gen.set_volume(0.7)


def play_scale():
    """Play C major scale up and down."""
    scale = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]

    # Ascending
    print("Playing ascending scale...")
    for note in scale:
        print(f"  {note}: {NOTES[note]:.2f} Hz")
        wave_gen.set_frequency(NOTES[note])
        wave_gen.set_amplitude(0.7)
        time.sleep(0.5)

    time.sleep(0.3)

    # Descending
    print("Playing descending scale...")
    for note in reversed(scale):
        print(f"  {note}: {NOTES[note]:.2f} Hz")
        wave_gen.set_frequency(NOTES[note])
        wave_gen.set_amplitude(0.7)
        time.sleep(0.5)

    # Fade out
    wave_gen.set_amplitude(0.0)
    time.sleep(2)


print("Musical Scale Demo - C Major")
print("Press Ctrl+C to stop")

App.run(user_loop=play_scale)
