#!/usr/bin/env python3
import time
import rtmidi
from hue_api import HueApi

def join_the_hue():
    api = HueApi()
    api.create_new_user("10.1.0.99")
    api.save_api_key("the_hue_is_due.dat")

def do_the_hue(api):
    api.load_existing("the_hue_is_due.dat")
    api.fetch_lights()
    api.fetch_groups()

def run_instructions(instructions):
    global api
    for i in instructions:
        group_name = i[1]
        brightness = int(i[2].strip())
        my_group = [j for j in api.groups if j.name == group_name][0]
        if brightness == 0:
            [j.set_off() for j in my_group.lights]
        else:
            [j.set_brightness(brightness) for j in my_group.lights]
            [j.set_on() for j in my_group.lights]

def callback(data, question_mark):
    message = data[0]
    if message[2] != 0:
        with open("./instructions.txt", "r") as f:
            instructions = [i.split(":") for i in f.readlines() if i[0] != '#']
        if len([i for i in instructions if i[0] == str(message[1])]) > 0:
            run_instructions([i for i in instructions if i[0] == str(message[1])])

api = HueApi()
do_the_hue(api)

if __name__ == "__main__":
    midi_in = rtmidi.MidiIn()
    midi_in.set_callback(callback)
    print(midi_in.get_ports())
    midi_in.open_port(1,name="Light Hub")

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
        midi_in.close_port()
        del midi_in
