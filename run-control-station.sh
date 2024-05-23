#!/bin/bash

# Kill all background processes on exit
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

python3 ./src/udp_sender.py &
python3 ./src/udp_receiver.py &
python3 ./src/webGUI.py &

# Keep this script alive forever
sleep infinity
