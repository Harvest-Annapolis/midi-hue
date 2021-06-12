#!/usr/bin/env python3
import time
import rtmidi
from hue_api import HueApi

def join_the_hue():
    api = HueApi()
    api.create_new_user("10.1.0.99")
    api.save_api_key("the_hue_is_due.dat")

def do_the_hue():
    api = HueApi()
    api.load_existing("the_hue_is_due.dat")
    api.fetch_lights()
    api.fetch_groups()
    [i.set_off() for i in api.groups[0].lights]
    time.sleep(5)
    [i.set_on() for i in api.groups[0].lights]

def callback(message, time):
    print(message)
    print(time)

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
            time.sleep(1)
    except KeyboardInterrupt:
        print('')
    finally:
        print("Exit.")
        midi_in.close_port()
        del midi_in
