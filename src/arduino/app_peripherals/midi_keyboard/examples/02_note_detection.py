# SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
#
# SPDX-License-Identifier: MPL-2.0

# EXAMPLE_NAME = Basic MIDI note detection

from arduino.app_peripherals.midi_keyboard import MIDIKeyboard
from arduino.app_utils import App

# Initialize MIDI keyboard (auto-detect first device)
midi = MIDIKeyboard()

# Display device info
print(f"Using MIDI device: {midi.device_name}")

# Register callbacks for note events
def on_note_on(note, velocity):
    freq = MIDIKeyboard.note_to_frequency(note)
    print(f"Note ON:  {note:3d} | Velocity: {velocity:3d} | Freq: {freq:7.2f} Hz")

def on_note_off(note, velocity):
    print(f"Note OFF: {note:3d} | Velocity: {velocity:3d}")

midi.on_note_on(on_note_on)
midi.on_note_off(on_note_off)

# Register callback for pitch bend
def on_pitch_bend(value):
    print(f"Pitch Bend: {value:6d} (range: -8192 to +8191)")

midi.on_pitch_bend(on_pitch_bend)

# Register callback for control changes
def on_cc(control, value):
    print(f"CC: {control:3d} | Value: {value:3d}")

midi.on_control_change(on_cc)

print("\nListening for MIDI events... Press Ctrl+C to exit.")
print("Play some notes or move controls on your MIDI controller.\n")

App.run()
