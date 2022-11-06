#!/usr/bin/env python3
from midi_map import midi_map
import base_appliance
import PySimpleGUI as sg

def format_instruction_string(instructions):
    output = "Midi Note: {} ({})\n\n".format(midi_map[int(instructions[0]["midi_note"])] ,instructions[0]["midi_note"])
    first = True
    for instruction in instructions:
        if not first:
            output += "\n"
        else:
            first = False

        if instruction["instruction_type"] == "light":
            output +=  "Lights: {} ({}%)".format(
                    instruction["args"][0],
                    int((int(instruction["args"][1])/255)*100),
                    instruction["midi_note"])
        elif instruction["instruction_type"] == "media":
            if instruction["args"][0] == "toggle":
                output += "Media: Play/Pause Audio"
            else:
                output += "Unknown Media Command"
    return output

def generate_button_map(row_width):
    rows=[]
    instructions = base_appliance.get_instructions()
    notes = sorted(list(set([i["midi_note"] for i in instructions])),reverse=True)
    for i in range(0, len(notes), row_width):
        rows.append([
            sg.Button(
                format_instruction_string([k for k in instructions if k["midi_note"] == j]), 
                font=("",10,"bold"), 
                size=(30,8),
                key=("button", j)) 
            for j in notes[i:i+row_width]])
    print(rows)
    return rows

if __name__ == "__main__":    
    layout = generate_button_map(4)
    
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
        if type(event) is tuple and"button" == event[0]:
            print(event[1])
        if event == sg.WIN_CLOSED:
            break
    
    window.close()


