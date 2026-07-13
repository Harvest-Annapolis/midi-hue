from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar

@dataclass
class InsAction:
    """Parent class for all action types that more than one value and/or have a user-specifiable range of values"""

class InsEnum(Enum):
    """Parent class for all action types that can be defined by an enum"""

@dataclass
class HueAction(InsAction):
    """Instruction Action class for setting a Hue lights group brightness to a value"""
    group_name: str
    brightness: int
    MAX_BRIGHTNESS: ClassVar[int] = 255

    @staticmethod
    def from_percent(group_name: str, brightness_pct: int) -> HueAction:
        brightness = int(HueAction.MAX_BRIGHTNESS * brightness_pct / 100)
        if brightness < 0:
            brightness = 0
        elif brightness > HueAction.MAX_BRIGHTNESS:
            brightness = HueAction.MAX_BRIGHTNESS
        return HueAction(group_name, brightness)
    
    def __str__(self) -> str:
        return f"Lights: {self.group_name} ({int(self.brightness / HueAction.MAX_BRIGHTNESS * 100)}%)"

class MediaAction(InsEnum):
    """Enum class for all media actions - currently just 'toggle'"""
    TOGGLE = 1

    def __str__(self) -> str:
        match self:
            case MediaAction.TOGGLE:
                return "Media: Play/Pause Audio"
            case _:
                return f"Unknown action: {self.name}"

@dataclass
class CameraPresetAction(InsAction):
    """Instruction Action class for setting a preset on the camera"""
    preset: int

    def __str__(self) -> str:
        return f"Camera Preset: {self.preset}"

class CameraAutotrackAction(InsEnum):
    """Instruction Action class for setting the autotrack setting on the camera"""
    FALSE = False
    TRUE = True

    def __str__(self) -> str:
        return f"Camera Auto-Track: {"on" if self == CameraAutotrackAction.TRUE else "off"}"

@dataclass
class Instruction:
    """Dataclass to represent one single midi instruction; one instruction can have zero or more actions"""
    description: str
    midi: int
    actions: list[InsAction | InsEnum]

    def action_strs(self) -> str:
        return "\n".join([str(action) for action in self.actions])
