# SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
#
# SPDX-License-Identifier: MPL-2.0

# EXAMPLE_NAME = List available MIDI devices

from arduino.app_peripherals.midi_keyboard import MIDIKeyboard

# List all available MIDI input devices
devices = MIDIKeyboard.list_usb_devices()

print("Available MIDI input devices:")
for i, device in enumerate(devices, 1):
    print(f"  {i}. {device}")

if not devices:
    print("  No MIDI devices found.")
    print("\nMake sure your MIDI controller is connected via USB.")

# List available controller profiles
profiles = MIDIKeyboard.list_profiles()

print("\nAvailable controller profiles:")
for profile in profiles:
    print(f"  - {profile}")
