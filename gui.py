#!/usr/bin/env python3
import base_appliance
import PySimpleGUI as sg
from instruction_classes import *

def format_instruction_string(instruction: Instruction) -> str:
    output = f"{instruction.description}\n\n"
    output += f"Midi Note: {_midi_map[instruction.midi]} ({instruction.midi})\n\n"
    output += instruction.action_strs()
    return output

def generate_button_map(row_buttons: int):
    rows = []
    config = base_appliance.get_config()
    button_config = config["gui"]["button_style"]
    instructions = base_appliance.get_instructions()

    notes = sorted(list(instructions.keys()))
    for i in range(0, len(notes), row_buttons):
        rows.append(
            [sg.Button(
                format_instruction_string(instructions[note]), 
                font = (button_config["font_family"],
                        button_config["font_size"],
                        button_config["font_style"]), 
                size = (button_config["button_width"],
                        button_config["button_height"]),
                key = ("button", note)
            ) for note in notes[i:i + row_buttons]
        ])
    
    [print([b.ButtonText.split("\n")[0] for b in r]) for r in rows]
    return rows

if __name__ == "__main__":
    global _midi_map

    base_appliance.load_configuration()
    config = base_appliance.get_config()
    _midi_map = config["midi"]["map"]
    gui_config = config["gui"]

    api = base_appliance.HueApi()
    base_appliance.do_the_hue(api) # TODO Reenable
    midi_in = base_appliance.init(api) # TODO Reenable
    
    layout = generate_button_map(gui_config["buttons_per_row"])
    
    # Create the window
    window = sg.Window(
            "Midi HUE Control Program", 
            layout, 
            size=(len(layout[0])*313,len(layout)*161), 
            resizable=True,
            use_default_focus=False)
    
    # Create an event loop
    while True:
        event, values = window.read()
        # End program if user closes window or
        # presses the OK button
        if type(event) is tuple and "button" == event[0]:
            base_appliance.callback(([0b10010000, event[1], 0b01111111], 0), "wat")
        if event == sg.WIN_CLOSED:
            base_appliance.cleanup(midi_in)
            break
    
    window.close()


