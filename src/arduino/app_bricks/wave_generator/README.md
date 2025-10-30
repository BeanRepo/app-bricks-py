# Wave Generator Brick

A continuous wave generator for real-time audio synthesis. Generates various waveforms (sine, square, sawtooth, triangle) and streams them to a USB speaker with smooth frequency and amplitude transitions.

## Features

- **Multiple waveforms**: sine, square, sawtooth, triangle
- **Smooth transitions**: Configurable glide (portamento), attack, and release times
- **Real-time control**: Change frequency, amplitude, and waveform on the fly
- **Efficient**: Pre-allocated buffers and NumPy vectorization
- **Thread-safe**: Safe to call from multiple threads

## Usage

### Basic Example

```python
from arduino.app_bricks.wave_generator import WaveGenerator
from arduino.app_utils import App

# Create wave generator with default settings
wave_gen = WaveGenerator()

# Start generation
App.start_brick(wave_gen)

# Control the generator
wave_gen.set_frequency(440.0)  # A4 note
wave_gen.set_amplitude(0.8)    # 80% amplitude

# Keep app running
App.run()
```

### Advanced Configuration

```python
from arduino.app_bricks.wave_generator import WaveGenerator
from arduino.app_utils import App

# Create with custom settings
wave_gen = WaveGenerator(
    sample_rate=16000,
    wave_type="square",       # Initial waveform
    block_duration=0.03,      # 30ms blocks
    attack=0.01,              # 10ms attack time
    release=0.03,             # 30ms release time
    glide=0.02,               # 20ms frequency glide
)

App.start_brick(wave_gen)

# Change waveform type
wave_gen.set_wave_type("triangle")

# Set frequency and amplitude
wave_gen.set_frequency(880.0)  # A5 note
wave_gen.set_amplitude(0.5)

# Adjust envelope
wave_gen.set_envelope_params(attack=0.05, release=0.1, glide=0.05)

App.run()
```

### Theremin-Style Controller

```python
import time
from arduino.app_bricks.wave_generator import WaveGenerator
from arduino.app_utils import App

wave_gen = WaveGenerator(wave_type="sine", glide=0.02)
App.start_brick(wave_gen)

def theremin_loop():
    """Simulate theremin-style frequency sweeps."""
    for freq in range(220, 880, 10):
        wave_gen.set_frequency(float(freq))
        wave_gen.set_amplitude(0.7)
        time.sleep(0.05)
    
    # Fade out
    wave_gen.set_amplitude(0.0)
    time.sleep(2)

App.run(user_loop=theremin_loop)
```

### With WebUI Control

```python
from arduino.app_bricks.wave_generator import WaveGenerator
from arduino.app_bricks.web_ui import WebUI
from arduino.app_utils import App

wave_gen = WaveGenerator()
ui = WebUI()

def on_frequency_change(sid, data):
    freq = float(data.get('frequency', 440))
    wave_gen.set_frequency(freq)

def on_amplitude_change(sid, data):
    amp = float(data.get('amplitude', 0.5))
    wave_gen.set_amplitude(amp)

def on_waveform_change(sid, data):
    wave_type = data.get('wave_type', 'sine')
    wave_gen.set_wave_type(wave_type)

ui.on_message('set_frequency', on_frequency_change)
ui.on_message('set_amplitude', on_amplitude_change)
ui.on_message('set_waveform', on_waveform_change)

App.run()
```

## API Reference

### Constructor

```python
WaveGenerator(
    sample_rate: int = 16000,
    wave_type: WaveType = "sine",
    block_duration: float = 0.03,
    attack: float = 0.01,
    release: float = 0.03,
    glide: float = 0.02,
    speaker_device: str = Speaker.USB_SPEAKER_1,
    speaker_format: str = "FLOAT_LE",
)
```

**Parameters:**
- `sample_rate`: Audio sample rate in Hz (default: 16000)
- `wave_type`: Initial waveform - "sine", "square", "sawtooth", "triangle" (default: "sine")
- `block_duration`: Audio block duration in seconds (default: 0.03)
- `attack`: Amplitude attack time in seconds (default: 0.01)
- `release`: Amplitude release time in seconds (default: 0.03)
- `glide`: Frequency glide time (portamento) in seconds (default: 0.02)
- `speaker_device`: Speaker device identifier (default: USB_SPEAKER_1)
- `speaker_format`: Audio format (default: "FLOAT_LE")

### Methods

#### `set_frequency(frequency: float)`
Set target output frequency with smooth glide transition.

**Parameters:**
- `frequency`: Target frequency in Hz (typically 20-8000 Hz)

#### `set_amplitude(amplitude: float)`
Set target output amplitude with smooth attack/release.

**Parameters:**
- `amplitude`: Target amplitude in range [0.0, 1.0]

#### `set_wave_type(wave_type: WaveType)`
Change the waveform type.

**Parameters:**
- `wave_type`: One of "sine", "square", "sawtooth", "triangle"

#### `set_volume(volume: float)`
Set master volume level.

**Parameters:**
- `volume`: Master volume in range [0.0, 1.0]

#### `set_envelope_params(attack=None, release=None, glide=None)`
Update envelope parameters.

**Parameters:**
- `attack`: Attack time in seconds (optional)
- `release`: Release time in seconds (optional)
- `glide`: Frequency glide time in seconds (optional)

#### `get_state() -> dict`
Get current generator state.

**Returns:**
- Dictionary with keys: `frequency`, `amplitude`, `wave_type`, `master_volume`, `phase`

## Waveform Types

### Sine Wave
Classic smooth sine wave, ideal for pure tones and musical applications.

```python
wave_gen.set_wave_type("sine")
```

### Square Wave
Sharp square wave with odd harmonics, creates a "hollow" or "clarinet-like" sound.

```python
wave_gen.set_wave_type("square")
```

### Sawtooth Wave
Bright sawtooth wave with all harmonics, creates a "buzzy" or "brassy" sound.

```python
wave_gen.set_wave_type("sawtooth")
```

### Triangle Wave
Softer than square, contains only odd harmonics with lower amplitude.

```python
wave_gen.set_wave_type("triangle")
```

## Envelope Parameters

### Attack Time
Time to rise from current amplitude to target amplitude when increasing.

**Typical values:**
- `0.001` - 1ms: Very fast, almost instant
- `0.01` - 10ms: Fast, percussive
- `0.1` - 100ms: Slow, pad-like

### Release Time
Time to fall from current amplitude to target amplitude when decreasing.

**Typical values:**
- `0.01` - 10ms: Short decay
- `0.05` - 50ms: Medium decay
- `0.5` - 500ms: Long decay, reverb-like

### Glide Time (Portamento)
Time to smoothly transition from current frequency to target frequency.

**Typical values:**
- `0.0` - Disabled: Instant frequency changes (may cause clicks)
- `0.005` - 5ms: Minimal, just removes clicks
- `0.02` - 20ms: Natural, smooth transitions (recommended)
- `0.05` - 50ms: Noticeable portamento effect
- `0.1+` - 100ms+: Very "slidey", theremin-like

## Hardware Requirements

- **Arduino UNO Q** (or compatible)
- **USB-C® hub** with external power
- **USB audio device** (USB speaker, wireless dongle, or USB-C → 3.5mm adapter)
- **Power supply** (5V, 3A) for USB hub

**Note:** Must run in **Network Mode** or **SBC Mode** as the USB-C port is needed for the hub.

## Troubleshooting

### No Sound Output
- Check USB speaker is connected and powered
- Verify amplitude is > 0: `wave_gen.set_amplitude(0.5)`
- Check master volume: `wave_gen.set_volume(0.8)`

### Choppy or Clicking Audio
- Increase glide time: `wave_gen.set_envelope_params(glide=0.05)`
- Reduce block duration for lower latency: `WaveGenerator(block_duration=0.02)`
- Close other CPU-intensive applications

### "No USB speaker found" Error
- Ensure USB-C hub is connected with 5V/3A power supply
- Connect USB audio device to the hub
- Restart the application

## License

This brick is licensed under the Mozilla Public License 2.0 (MPL-2.0).

Copyright (C) 2025 ARDUINO SA <http://www.arduino.cc>
