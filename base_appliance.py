#!/usr/bin/env python3
import time
import tomllib
import rtmidi
import requests
from hue_api import HueApi
from instruction_classes import *
from midi import *
import win32api
from win32con import VK_MEDIA_PLAY_PAUSE, KEYEVENTF_EXTENDEDKEY

_config = None
_instructions = None
_hue_api = None

#
# Configuration File-related Functions
#

def load_configuration():
    global _config
    # Import config file data - TOML file needs to be opened with RB (read binary) mode
    with open("config.toml", "rb") as config_toml:
        _config = tomllib.load(config_toml)
        print("Loaded config.toml")

    # Get the path to the instructions file from the configured value
    instructions_path = _config["instructions_path"]
    with open(instructions_path, "rb") as instructions_toml:
        instructions_data = tomllib.load(instructions_toml)["instructions"]
        print(f"Loaded {instructions_path}")
    process_instructions(instructions_data)

def process_instructions(instructions_data: dict) -> list[Instruction]:
    """Parse data into appropriate data structures"""
    global _config, _instructions
    inst_list = []
    # Parse each instruction
    for instruction in instructions_data:
        actions = []
        # Lights
        if "lights" in instruction:
            # Go through each lights group from the config
            inst_lights = instruction["lights"]
            lights_list = []
            for toml_name, hue_name in _config["hue_groups"].items():
                if toml_name in inst_lights:
                    # TODO: Future possibility to support brightnesses. I built it into the data structure but don't feel like figuring out the parsing logic here
                    # TODO: Other properties could also be supported here like color or temperature, but are not implemented right now.
                    lights_list.append(HueAction(hue_name, inst_lights[toml_name]["brightness"]))
            actions.extend(lights_list)
        # Misc
        if "misc" in instruction:
            # Currently only can be the media action, which can only be the toggle. Still add parsing logic though
            inst_misc = instruction["misc"]
            misc_list = []
            # Parse media actions
            if "media" in inst_misc:
                match inst_misc["media"]:
                    case "toggle":
                        misc_list.append(MediaAction.TOGGLE)
                    case _:
                        print(f"Unknown media action {inst_misc["media"]}!")
            actions.extend(misc_list)
        # Camera
        if "camera" in instruction:
            # Add any camera actions to the lists
            inst_camera = instruction["camera"]
            camera_list = []
            if "preset" in inst_camera:
                camera_list.append(CameraPresetAction(inst_camera["preset"]))
            if "autotrack" in inst_camera:
                camera_list.append(CameraAutotrackAction(inst_camera["autotrack"]))
            actions.extend(camera_list)
        # Put all generated actions into an Instruction class
        inst_list.append(Instruction(instruction["description"], instruction["midi"], actions))
    _instructions = inst_list
    print("Parsed instructions list")

def get_config() -> dict | None:
    global _config
    if _config is None:
        print("Error - config is not yet loaded! Please make sure load_configuration is run before get_config")
    return _config

def get_instructions() -> list[Instruction] | None:
    global _instructions
    if _instructions is None:
        print("Error - instructions is not yet loaded and/or parsed! Please make sure load_configuration is run before get_instructions")
    return _instructions

#
# Instruction Execution Functions
#

def run_instruction(instruction: Instruction):
    for action in instruction.actions:
        match action:
            case HueAction():
                perform_hue_action(action)
            case MediaAction():
                perform_media_action(action)
            case CameraPresetAction() |\
                 CameraAutotrackAction():
                pass
            case _:
                print("Invalid Instruction Type!!!")
                print(f"Object received: {action}")

def perform_hue_action(action: HueAction):
    global _hue_api
    group = [g for g in _hue_api.groups if g.name == action.group_name][0]
    if action.brightness == 0:
        [l.set_off() for l in group.lights]
    else:
        [l.set_on() for l in group.lights]
        [l.set_brightness(action.brightness) for l in group.lights] # TODO: See if we can swap the order of these

def perform_media_action(action: MediaAction):
    match action.value:
        case MediaAction.TOGGLE:
            win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY, 0)
        case _:
            print(f"Unknown media action type: {action}")

def perform_camera_action(action: CameraPresetAction | CameraAutotrackAction):
    match action:
        case CameraPresetAction():
            requests.post("http://10.2.0.93/cgi-bin/ptzctrl.cgi?post_preset", data="poscallwithspeed={}&panspeed=10&tiltspeed=10&zoomspeed=5".format(action.preset))
        case CameraAutotrackAction():
            onoff = 2 if action == CameraAutotrackAction.TRUE else 3
            requests.get("http://10.2.0.93/cgi-bin/ptzctrl.cgi?post_image_value&autotrack&{}".format(onoff), data="")
        case _:
            print("How'd you get in here???")
            print("I mean uhhh")
            print(f"Unknown camera action: {action}")

#
# Clean this up later
#

def join_the_hue():
    api = HueApi()
    api.create_new_user("10.1.0.99")
    api.save_api_key("the_hue_is_due.dat")

def do_the_hue(api):
    api.load_existing("the_hue_is_due.dat")
    api.fetch_lights()
    api.fetch_groups()

# Args: (Midi Data, Delta Time), Optional Data Value from Callback Init Time
def callback(data, _):
    (raw_message, _) = data
    message = MidiMessage.from_message(raw_message)
    match message.type:
        case MidiMessageType.NOTE_ON:
            if message.data_2 != 0: # If velocity is not 0:
                instructions = get_instructions()
                [run_instruction(i) for i in instructions if i.midi == message.data_1]
        case _:
            pass
            # No other message types supported at present

def init(api):
    global _hue_api
    midi_in = rtmidi.MidiIn()
    _hue_api = api
    midi_in.set_callback(callback)
    print(midi_in.get_ports())
    midi_in.open_port(1,name="Light Hub")
    return midi_in

def cleanup(midi_in):
    midi_in.close_port()
    del midi_in

if __name__ == "__main__":
    load_configuration()
    [print(i) for i in get_instructions()]

    api = HueApi()
    do_the_hue(api)
    
    midi_in = init(api)
            
    print("Entering main loop. Press Control-C to exit.")
    try:
        # Just wait for keyboard interrupt,
        # everything else is handled via the input callback.
        while True:
            cmd=input("Run manual command>>>")
            callback(([0b10010000,cmd,0b01111111], 0), "wat")
    except KeyboardInterrupt:
        print('')
    finally:
        print("Exit.")
        cleanup(midi_in)
