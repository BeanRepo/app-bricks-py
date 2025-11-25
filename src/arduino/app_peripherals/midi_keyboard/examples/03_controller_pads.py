# SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
#
# SPDX-License-Identifier: MPL-2.0

# EXAMPLE_NAME = Controller pads with semantic mapping

from arduino.app_peripherals.midi_keyboard import MIDIKeyboard
from arduino.app_utils import App

# Initialize with a controller profile
# Try different profiles: "akai_mpc_mini", "akai_mpk_mini_plus", "ni_maschine_mikro"
midi = MIDIKeyboard(profile="akai_mpc_mini")

# Display profile info
profile_info = midi.get_profile_info()
print(f"Using profile: {profile_info['name']}")
print(f"Pad mapping: {len(profile_info['note_map'])} pads")
print(f"Knob mapping: {len(profile_info['cc_map'])} knobs")
print()

# Register semantic callbacks for pads
for i in range(1, 17):
    pad_name = f"pad_{i}"
    
    def make_callback(pad):
        return lambda velocity: print(f"{pad:10s} hit! Velocity: {velocity:3d}")
    
    midi.on_pad(pad_name, make_callback(pad_name))

# Register semantic callbacks for knobs
for i in range(1, 9):
    knob_name = f"knob_{i}"
    
    def make_callback(knob):
        return lambda value: print(f"{knob:10s} turned to: {value:3d}")
    
    try:
        midi.on_knob(knob_name, make_callback(knob_name))
    except Exception:
        pass  # Knob not in profile

print("Listening for pad and knob events... Press Ctrl+C to exit.")
print("Hit pads or turn knobs on your controller.\n")

App.run()
