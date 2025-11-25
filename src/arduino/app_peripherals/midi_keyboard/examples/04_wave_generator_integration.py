# SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
#
# SPDX-License-Identifier: MPL-2.0

# EXAMPLE_NAME = MIDI-controlled wave generator synthesizer
# EXAMPLE_REQUIRES = WaveGenerator brick

from arduino.app_bricks.wave_generator import WaveGenerator
from arduino.app_peripherals.midi_keyboard import MIDIKeyboard
from arduino.app_utils import App

# Initialize wave generator
wave_gen = WaveGenerator(
    wave_type="sawtooth",
    glide=0.02,  # 20ms glide for smooth transitions
    attack=0.01,
    release=0.05,
)

# Initialize MIDI keyboard
midi = MIDIKeyboard()

print(f"MIDI Synth ready!")
print(f"Device: {midi.device_name}")
print(f"Waveform: {wave_gen.wave_type}")
print()

# Track active notes for monophonic playback with last-note priority
active_notes = []

def on_note_on(note, velocity):
    """Handle note on: start playing the note."""
    active_notes.append(note)
    
    # Convert MIDI note to frequency
    freq = MIDIKeyboard.note_to_frequency(note)
    
    # Set frequency and amplitude based on velocity
    wave_gen.set_frequency(freq)
    wave_gen.set_amplitude(velocity / 127.0)
    
    print(f"♪ Note ON:  {note:3d} ({freq:7.2f} Hz) | Velocity: {velocity:3d}")

def on_note_off(note, velocity):
    """Handle note off: stop playing or switch to previous note."""
    if note in active_notes:
        active_notes.remove(note)
    
    if active_notes:
        # Still have notes pressed, play the most recent one
        last_note = active_notes[-1]
        freq = MIDIKeyboard.note_to_frequency(last_note)
        wave_gen.set_frequency(freq)
        print(f"♪ Note OFF: {note:3d} → switching to {last_note:3d}")
    else:
        # No notes pressed, fade out
        wave_gen.set_amplitude(0.0)
        print(f"♪ Note OFF: {note:3d} → silence")

def on_pitch_bend(value):
    """Handle pitch bend: modulate frequency."""
    # Pitch bend range: ±2 semitones (±200 cents)
    bend_factor = 1.0 + (value / 8192.0) * 0.1  # ±10% frequency change
    current_freq = wave_gen._current_freq
    new_freq = current_freq * bend_factor
    wave_gen.set_frequency(new_freq)
    print(f"↕ Pitch bend: {value:6d}")

def on_cc(control, value):
    """Handle control changes: map to synth parameters."""
    if control == 1:  # Modulation wheel → glide time
        glide = value / 127.0 * 0.1  # 0-100ms
        wave_gen.set_envelope_params(glide=glide)
        print(f"◎ Modulation → Glide: {glide*1000:.1f}ms")
    
    elif control == 7:  # Volume → master amplitude
        # This could control a volume multiplier
        print(f"♫ Volume: {value:3d}")
    
    elif control == 74:  # Filter cutoff → attack time
        attack = value / 127.0 * 0.2  # 0-200ms
        wave_gen.set_envelope_params(attack=attack)
        print(f"⚡ Attack time: {attack*1000:.1f}ms")
    
    elif control == 71:  # Resonance → release time
        release = value / 127.0 * 0.5  # 0-500ms
        wave_gen.set_envelope_params(release=release)
        print(f"⚡ Release time: {release*1000:.1f}ms")

# Register MIDI callbacks
midi.on_note_on(on_note_on)
midi.on_note_off(on_note_off)
midi.on_pitch_bend(on_pitch_bend)
midi.on_control_change(on_cc)

print("Play your MIDI keyboard to control the synthesizer!")
print("- Notes: Control pitch and trigger sound")
print("- Pitch Bend: Modulate frequency")
print("- CC 1 (Mod Wheel): Glide time")
print("- CC 74: Attack time")
print("- CC 71: Release time")
print("\nPress Ctrl+C to exit.\n")

App.run()
