#!/bin/bash
python3 -m pip install -r requirements.txt
python3 << BUILD
import server
server.join_the_hue()
BUILD
