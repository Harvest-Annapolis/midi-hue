from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class MidiMessageType(Enum):
  NOTE_OFF = 0b1000
  NOTE_ON = 0b1001
  POLYPHONIC_AFTERTOUCH = 0b1010
  CONTROL_CHANGE = 0b1011
  PROGRAM_CHANGE = 0b1100
  CHANNEL_AFTERTOUCH = 0b1101
  PITCH_WHEEL = 0b1110
  SYSTEM_EXCLUSIVE = 0b1111

@dataclass
class MidiMessage:
  # 0b1tttnnnn 0xxxxxxx 0yyyyyyy
  type: MidiMessageType
  channel: int
  data_1: int
  data_2: int

  def __init__(self, byte_0: int, byte_1: int, byte_2: int):
    self.type = MidiMessageType(byte_0 >> 4)
    self.channel = byte_0 & 0b1111
    self.data_1 = byte_1 & 0b01111111
    self.data_2 = byte_2 & 0b01111111

  @staticmethod
  def from_message(message) -> MidiMessage:
    return MidiMessage(message[0], message[1], message[2])
