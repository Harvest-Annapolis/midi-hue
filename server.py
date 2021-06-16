#!/usr/bin/env python3
import time
import rtmidi
from hue_api import HueApi

api = HueApi()
do_the_hue(api)

def join_the_hue():
    api = HueApi()
    api.create_new_user("10.1.0.99")
    api.save_api_key("the_hue_is_due.dat")

def do_the_hue(api):
    api.load_existing("the_hue_is_due.dat")
    api.fetch_lights()
    api.fetch_groups()
    #[i.set_off() for i in api.groups[0].lights]
    #time.sleep(5)
    #[i.set_on() for i in api.groups[0].lights]

def run_instruction(instructions):
    for i in instructions:
        group_name = i[1]
        brightness = i[2]
        if brightness = 0:
            [i.set_off() for i in api.groups[0].lights]
        else:
            [i.set_brightness(brightness) for i in api.groups[0].lights]
            [i.set_on() for i in api.groups[0].lights]

def callback(message, time):
    if message[2] != 0:
        print(message)
        with open("./instructions.txt", "r") as f:
            instructions = [i.split(":") for i in f.readlines() if i[0] != '#']
        if len([i for i in instructions if i[0] == message[1]]) > 0:
            run_instructions([i for i in instructions if i[0] == str(message[1])])

if __name__ == "__main__":
    midi_in = rtmidi.MidiIn()
    midi_in.set_callback(callback)
    print(midi_in.get_ports())
    midi_in.open_port(0,name="Light Hub")

    print("Entering main loop. Press Control-C to exit.")
    try:
        # Just wait for keyboard interrupt,
        # everything else is handled via the input callback.
        while True:
            cmd=input("Run manual command>>>")
            callback([144,cmd,127], 0)
    except KeyboardInterrupt:
        print('')
    finally:
        print("Exit.")
        midi_in.close_port()
        del midi_in
