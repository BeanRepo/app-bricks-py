# SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
#
# SPDX-License-Identifier: MPL-2.0

"""MIDI controller profiles for semantic event mapping."""

from typing import Dict, Optional


class MIDIProfile:
    """Base class for MIDI controller profiles.

    Profiles provide semantic mapping between raw MIDI note/CC numbers
    and human-readable control names (e.g., note 36 -> "kick", CC 70 -> "knob_1").
    """

    def __init__(self):
        self.name = "Generic"
        self.note_map: Dict[int, str] = {}  # note_number -> semantic_name
        self.cc_map: Dict[int, str] = {}    # cc_number -> semantic_name
        self.has_aftertouch = False
        self.has_pitchbend = False


class AkaiMPKMiniPlusProfile(MIDIProfile):
    """Profile for Akai MPK Mini Plus keyboard controller."""

    def __init__(self):
        super().__init__()
        self.name = "Akai MPK Mini Plus"

        # 25-key keyboard (C2-C4, notes 48-72)
        # No semantic mapping for keyboard notes - passthrough

        # 8 pad (Bank A: C1-G#1, notes 36-43)
        self.note_map = {
            36: "pad_1", 37: "pad_2", 38: "pad_3", 39: "pad_4",
            40: "pad_5", 41: "pad_6", 42: "pad_7", 43: "pad_8",
        }

        # 8 knob (CC 70-77)
        self.cc_map = {
            70: "knob_1", 71: "knob_2", 72: "knob_3", 73: "knob_4",
            74: "knob_5", 75: "knob_6", 76: "knob_7", 77: "knob_8",
            1: "modwheel",
        }

        self.has_aftertouch = False
        self.has_pitchbend = True


class AkaiMPCMiniProfile(MIDIProfile):
    """Profile for Akai MPC Mini / MPC Mini Play drum pad controller."""

    def __init__(self):
        super().__init__()
        self.name = "Akai MPC Mini"

        # 16 pad (Bank A: C1-D#2, notes 36-51)
        self.note_map = {
            36: "pad_1",  37: "pad_2",  38: "pad_3",  39: "pad_4",
            40: "pad_5",  41: "pad_6",  42: "pad_7",  43: "pad_8",
            44: "pad_9",  45: "pad_10", 46: "pad_11", 47: "pad_12",
            48: "pad_13", 49: "pad_14", 50: "pad_15", 51: "pad_16",
        }

        # Bank B (D2-F#2, notes 52-67)
        for i in range(16):
            self.note_map[52 + i] = f"pad_b_{i + 1}"

        # 8 knob (CC 70-77 by default, user-configurable)
        self.cc_map = {
            70: "knob_1", 71: "knob_2", 72: "knob_3", 73: "knob_4",
            74: "knob_5", 75: "knob_6", 76: "knob_7", 77: "knob_8",
        }

        self.has_aftertouch = False
        self.has_pitchbend = False


class NIMaschineMikroProfile(MIDIProfile):
    """Profile for Native Instruments Maschine Mikro MK3 controller.

    Note: This profile is for MIDI mode. In Maschine mode, the controller
    uses proprietary protocol and will not send standard MIDI messages.
    """

    def __init__(self):
        super().__init__()
        self.name = "NI Maschine Mikro MK3"

        # 16 RGB pad (C1-D#2, notes 36-51 in MIDI mode)
        self.note_map = {
            36: "pad_1",  37: "pad_2",  38: "pad_3",  39: "pad_4",
            40: "pad_5",  41: "pad_6",  42: "pad_7",  43: "pad_8",
            44: "pad_9",  45: "pad_10", 46: "pad_11", 47: "pad_12",
            48: "pad_13", 49: "pad_14", 50: "pad_15", 51: "pad_16",
        }

        # Controls (configurable in MIDI mode)
        self.cc_map = {
            22: "encoder",      # Main encoder
            1: "touch_strip",   # Touch strip (can also send pitch bend)
        }

        self.has_aftertouch = True  # Polyphonic aftertouch on pads
        self.has_pitchbend = True


class LaunchpadMiniProfile(MIDIProfile):
    """Profile for Novation Launchpad Mini grid controller."""

    def __init__(self):
        super().__init__()
        self.name = "Novation Launchpad Mini"

        # 8x8 grid (64 pads)
        self.note_map = {}
        for row in range(8):
            for col in range(8):
                note = row * 16 + col  # Launchpad uses 16-column addressing
                self.note_map[note] = f"pad_{row}_{col}"

        # Side buttons (CC)
        for i in range(8):
            self.cc_map[104 + i] = f"side_button_{i}"

        # Top buttons (notes)
        for i in range(8):
            self.note_map[104 + i] = f"top_button_{i}"

        self.has_aftertouch = False
        self.has_pitchbend = False


class GeneralMIDIDrumMapProfile(MIDIProfile):
    """Profile using General MIDI drum map for semantic naming."""

    def __init__(self):
        super().__init__()
        self.name = "General MIDI Drum Map"

        # Standard GM drum assignments
        self.note_map = {
            35: "kick_acoustic",
            36: "kick",           # Bass Drum 1
            37: "side_stick",
            38: "snare_acoustic",
            39: "clap",
            40: "snare_electric",
            41: "tom_low_floor",
            42: "hihat_closed",
            43: "tom_low",
            44: "hihat_pedal",
            45: "tom_mid",
            46: "hihat_open",
            47: "tom_mid_low",
            48: "tom_mid_high",
            49: "crash_1",
            50: "tom_high",
            51: "ride_1",
            52: "chinese",
            53: "ride_bell",
            54: "tambourine",
            55: "splash",
            56: "cowbell",
            57: "crash_2",
            58: "vibraslap",
            59: "ride_2",
        }

        self.cc_map = {}
        self.has_aftertouch = False
        self.has_pitchbend = False


# Profile registry
_PROFILES = {
    "generic": MIDIProfile,
    "akai_mpk_mini_plus": AkaiMPKMiniPlusProfile,
    "akai_mpc_mini": AkaiMPCMiniProfile,
    "ni_maschine_mikro": NIMaschineMikroProfile,
    "launchpad_mini": LaunchpadMiniProfile,
    "gm_drums": GeneralMIDIDrumMapProfile,
}


def load_profile(profile_name: str) -> MIDIProfile:
    """Load a MIDI controller profile by name.

    Args:
        profile_name: Profile identifier (e.g., "akai_mpc_mini")

    Returns:
        MIDIProfile instance

    Raises:
        ValueError: If profile name is unknown
    """
    if profile_name not in _PROFILES:
        raise ValueError(
            f"Unknown profile '{profile_name}'. Available: {list(_PROFILES.keys())}"
        )
    return _PROFILES[profile_name]()


def list_available_profiles() -> list:
    """List all available profile names.

    Returns:
        List of profile name strings
    """
    return list(_PROFILES.keys())


def detect_profile(device_name: str) -> str:
    """Auto-detect controller profile from MIDI device name.

    Args:
        device_name: MIDI device name from mido.get_input_names()

    Returns:
        Profile name (best match or "generic")
    """
    device_lower = device_name.lower()

    # Signature matching
    signatures = {
        "mpk mini": "akai_mpk_mini_plus",
        "mpk mini 3": "akai_mpk_mini_plus",
        "mpc mini": "akai_mpc_mini",
        "maschine mikro": "ni_maschine_mikro",
        "launchpad mini": "launchpad_mini",
    }

    for signature, profile in signatures.items():
        if signature in device_lower:
            return profile

    return "generic"
