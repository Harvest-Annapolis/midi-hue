#!/usr/bin/env python3
import time
import rtmidi
from hue_api import HueApi
import win32api
from win32con import VK_MEDIA_PLAY_PAUSE, KEYEVENTF_EXTENDEDKEY

_internal_api = None

def join_the_hue():
    api = HueApi()
    api.create_new_user("10.1.0.99")
    api.save_api_key("the_hue_is_due.dat")

def do_the_hue(api):
    api.load_existing("the_hue_is_due.dat")
    api.fetch_lights()
    api.fetch_groups()

def light_instruction(group_name, brightness):
    my_group = [j for j in _internal_api.groups if j.name == group_name][0]
    if brightness == 0:
        [j.set_off() for j in my_group.lights]
    else:
        [j.set_on() for j in my_group.lights]
        [j.set_brightness(brightness) for j in my_group.lights]

def run_instructions(instructions):
    global _internal_api
    for i in instructions:
        if i["instruction_type"] == "light":
            light_instruction(i["args"][0].strip(), int(i["args"][1].strip()))
        elif i["instruction_type"] == "media":
            media_cues(i["args"][0].strip())
        else:
            print("Invalid Instruction Type!!!")
        
def media_cues(cue):
    if cue == "toggle":
        win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY, 0)

def get_instructions():
    with open("./instructions.txt", "r") as f:
        instructions = [i.split(":") for i in f.readlines() if i[0] != '#' and i.strip() != ""]
        instructions = [{"midi_note":i[0], "instruction_type":i[1], "args":i[2:]} for i in instructions]
    return instructions
 
def callback(data, question_mark):
    message = data[0]
    if message[2] != 0:
        instructions = get_instructions()
        if len([i for i in instructions if i["midi_note"] == str(message[1])]) > 0:
            run_instructions([i for i in instructions if i["midi_note"] == str(message[1])])

def init(api):
    global _internal_api
    midi_in = rtmidi.MidiIn()
    _internal_api = api
    midi_in.set_callback(callback)
    print(midi_in.get_ports())
    midi_in.open_port(1,name="Light Hub")
    return midi_in

def cleanup(midi_in):
    midi_in.close_port()
    del midi_in

if __name__ == "__main__":
    api = HueApi()
    do_the_hue(api)
    
    midi_in = init(api)

    with open("./instructions.txt", "r") as f:
        instructions = f.read()
        print("{}\n".format(instructions))
            
    print("Entering main loop. Press Control-C to exit.")
    try:
        # Just wait for keyboard interrupt,
        # everything else is handled via the input callback.
        while True:
            cmd=input("Run manual command>>>")
            callback(([144,cmd,127], 0), "wat")
    except KeyboardInterrupt:
        print('')
    finally:
        print("Exit.")
        cleanup(midi_in)
