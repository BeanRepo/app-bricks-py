# MIDI Keyboard Peripheral

This peripheral allows you to receive input from MIDI keyboards, drum pads, and control surfaces via USB MIDI.

## Overview

The MIDI Keyboard peripheral allows you to:

- Receive note on/off events from MIDI keyboards and drum pads
- Read control change (CC) messages from knobs, faders, and buttons
- Handle pitch bend, aftertouch, and other MIDI messages
- Use controller profiles for semantic event mapping
- Convert MIDI note numbers to audio frequencies

It supports any USB MIDI device that appears as a standard MIDI input on Linux, including keyboards, drum pad controllers, grid controllers, and general MIDI control surfaces.

## Prerequisites

Before using the MIDI Keyboard peripheral, ensure you have the following:

- USB-C® Hub with external power supply (5V, 3A)
- USB MIDI keyboard, controller, or drum pad
- Arduino UNO Q running in Network Mode or SBC Mode (USB-C port needed for the hub)

Tips:
- Most modern MIDI controllers use USB MIDI and will work without drivers on Linux
- Some controllers have multiple modes (MIDI mode vs. proprietary mode) - ensure MIDI mode is enabled
- The peripheral will auto-detect the first available MIDI device if none is specified

## Features

- Auto-detection of USB MIDI devices
- Multiple callback types: note on/off, control change, pitch bend, aftertouch
- Controller profiles for semantic pad/knob mapping
- Support for MIDI channels (1-16) filtering
- MIDI note to frequency conversion utilities
- Thread-safe event handling
- Context manager support for automatic start/stop

## Code example and usage

Here is a basic example for detecting MIDI notes:

```python
from arduino.app_peripherals.midi_keyboard import MIDIKeyboard
from arduino.app_utils import App

midi = MIDIKeyboard()

def on_note_on(note, velocity):
    freq = MIDIKeyboard.note_to_frequency(note)
    print(f"Note {note}: {freq:.2f} Hz, velocity {velocity}")

def on_note_off(note, velocity):
    print(f"Note {note} released")

midi.on_note_on(on_note_on)
midi.on_note_off(on_note_off)

App.run()
```

You can filter by MIDI channel and handle control changes:

```python
midi = MIDIKeyboard(channel=1)  # Listen only to channel 1

def on_cc(control, value):
    if control == 1:  # Modulation wheel
        print(f"Modulation: {value}")
    elif control == 7:  # Volume
        print(f"Volume: {value}")

midi.on_control_change(on_cc)

App.run()
```

For drum pad controllers, use profiles for semantic mapping:

```python
from arduino.app_peripherals.midi_keyboard import MIDIKeyboard
from arduino.app_utils import App

# Use controller profile for semantic pad names
midi = MIDIKeyboard(profile="akai_mpc_mini")

# Register callback for specific pads
midi.on_pad("pad_1", lambda vel: print(f"Kick drum: {vel}"))
midi.on_pad("pad_2", lambda vel: print(f"Snare drum: {vel}"))
midi.on_pad("pad_3", lambda vel: print(f"Hi-hat: {vel}"))

# Register callback for knobs
midi.on_knob("knob_1", lambda val: print(f"Filter cutoff: {val}"))

App.run()
```

## Controller Profiles

The peripheral includes built-in profiles for common MIDI controllers:

### Available Profiles

- `generic` - Generic MIDI device (no semantic mapping)
- `akai_mpk_mini_plus` - Akai MPK Mini Plus keyboard controller
- `akai_mpc_mini` - Akai MPC Mini drum pad controller
- `ni_maschine_mikro` - Native Instruments Maschine Mikro MK3 (MIDI mode)
- `launchpad_mini` - Novation Launchpad Mini grid controller
- `gm_drums` - General MIDI drum map for semantic drum names

### Profile Usage

Profiles map raw MIDI note/CC numbers to semantic names:

```python
# Without profile - raw MIDI
midi = MIDIKeyboard()
midi.on_note_on(lambda note, vel: print(f"Note {note}"), note=36)

# With profile - semantic names
midi = MIDIKeyboard(profile="akai_mpc_mini")
midi.on_pad("pad_1", lambda vel: print(f"Pad 1"))  # Automatically maps to note 36
```

### Checking Profile Info

```python
midi = MIDIKeyboard(profile="akai_mpc_mini")
info = midi.get_profile_info()

print(f"Profile: {info['name']}")
print(f"Pads: {info['note_map']}")
print(f"Knobs: {info['cc_map']}")
print(f"Has aftertouch: {info['has_aftertouch']}")
print(f"Has pitch bend: {info['has_pitchbend']}")
```

## Integration with Wave Generator

The MIDI Keyboard peripheral integrates seamlessly with the Wave Generator brick for synthesizer control:

```python
from arduino.app_bricks.wave_generator import WaveGenerator
from arduino.app_peripherals.midi_keyboard import MIDIKeyboard
from arduino.app_utils import App

wave_gen = WaveGenerator(wave_type="sawtooth", glide=0.02)
midi = MIDIKeyboard()

active_notes = []

def on_note_on(note, velocity):
    active_notes.append(note)
    freq = MIDIKeyboard.note_to_frequency(note)
    wave_gen.set_frequency(freq)
    wave_gen.set_amplitude(velocity / 127.0)

def on_note_off(note, velocity):
    if note in active_notes:
        active_notes.remove(note)
    if not active_notes:
        wave_gen.set_amplitude(0.0)

midi.on_note_on(on_note_on)
midi.on_note_off(on_note_off)

App.run()
```

## Understanding MIDI Messages

### Note Messages

MIDI notes are numbered 0-127, where middle C (C4) is note 60. The `note_to_frequency()` method converts note numbers to audio frequencies using standard tuning (A4 = 440 Hz).

**Velocity** represents how hard a key or pad is pressed, with values from 0 (lightest) to 127 (hardest). Many controllers use this for dynamic expression.

### Control Change (CC)

Control Change messages carry values from 0-127 and are sent by knobs, faders, and buttons. Some CC numbers have standard meanings:
- CC 1: Modulation wheel
- CC 7: Volume
- CC 10: Pan
- CC 64: Sustain pedal

Most controllers allow you to configure which CC numbers are sent by each knob or fader.

### Pitch Bend

Pitch bend messages have a range of -8192 to +8191 (14-bit resolution) and are typically used for smooth pitch modulation. The bend range (how many semitones the full range represents) is controller-dependent but typically ±2 semitones.

## API Reference

### Constructor

```python
MIDIKeyboard(
    device: str = USB_MIDI_1,
    channel: int = None,
    profile: str = None,
)
```

**Parameters:**
- `device`: MIDI device name or USB_MIDI_1/2 macro (default: USB_MIDI_1)
- `channel`: MIDI channel filter 1-16, None for all channels (default: None)
- `profile`: Controller profile name for semantic mapping (default: None)

### Callback Registration Methods

#### `on_note_on(callback, note=None)`
Register callback for note on events.
- If `note` is None: `callback(note, velocity)` receives all note on events
- If `note` is specified: `callback(velocity)` receives only that note

#### `on_note_off(callback, note=None)`
Register callback for note off events.

#### `on_control_change(callback, control=None)`
Register callback for control change events.
- If `control` is None: `callback(control, value)` receives all CC events
- If `control` is specified: `callback(value)` receives only that CC

#### `on_pitch_bend(callback)`
Register callback for pitch bend events: `callback(value)` where value is -8192 to +8191

#### `on_aftertouch(callback)`
Register callback for aftertouch (channel pressure) events: `callback(value)` where value is 0-127

#### `on_pad(pad_name, callback)`
Register callback for semantic pad name (requires profile): `callback(velocity)`

#### `on_knob(knob_name, callback)`
Register callback for semantic knob name (requires profile): `callback(value)`

### Utility Methods

#### `note_to_frequency(note: int) -> float`
Convert MIDI note number to frequency in Hz.

#### `frequency_to_note(frequency: float) -> int`
Convert frequency in Hz to nearest MIDI note number.

#### `list_usb_devices() -> list`
List all available MIDI input devices.

#### `list_profiles() -> list`
List all available controller profile names.

#### `get_profile_info() -> dict`
Get current profile information (note map, CC map, features).

## License

This peripheral is licensed under the Mozilla Public License 2.0 (MPL-2.0).

Copyright (C) ARDUINO SRL <http://www.arduino.cc>
