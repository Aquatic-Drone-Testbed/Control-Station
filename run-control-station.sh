#!/bin/bash

# Kill all background processes on exit
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

python3 ./src/control_station.py &
python3 ./src/webGUI.py &

# Keep this script alive forever
while true; do sleep 86400; done
