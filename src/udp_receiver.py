import socket
import numpy as np
import cv2
import asyncio
import websockets
import threading
import queue
import json

# Constants for easy adjustments
GPS_PORT = 9001
VIDEO_PORT = 9002
RADAR_PORT = 9003
SLAM_PORT = 9004
DIAGNOSTIC_PORT = 20000
BUFFER_SIZE = 65535

# Create a queue for thread-safe image transfer
image_queue = queue.Queue()
diagnostics_queue = queue.Queue()

camera_status = False
gps_status = "Disconnected"
thruster_status = False
IMU_status = False
radar_status = "Disconnected"
pi_status = "Disconnected"

# Function to receive and decode video data from boat
def receive_camera_video():   
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('', VIDEO_PORT))
        print(f"Listening for video on port {VIDEO_PORT}...")
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            print(f"Received video packet from {addr}, {len(data)} bytes")
            img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            if img is not None:
                # Put the image into the queue instead of displaying it directly
                image_queue.put(('camera', img))
                image_queue.put(('_radar', img))
                image_queue.put(('__slam', img))
            else:
                print("Could not decode video data")

def receive_radar_video():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('', RADAR_PORT))
        print(f"Listening for radar on port {RADAR_PORT}...")
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            print(f"Received radar packet from {addr}, {len(data)} bytes")
            img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            if img is not None:
                image_queue.put(('_radar', img))
            else:
                print("Could not decode radar data")

def receive_slam_video():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('', SLAM_PORT))
        print(f"Listening for SLAM on port {SLAM_PORT}...")
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            print(f"Received SLAM packet from {addr}, {len(data)} bytes")
            img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            if img is not None:
                image_queue.put(('__slam', img))
            else:
                print("Could not decode SLAM data")

async def send_data(websocket):
    print("start send_data()...")
    try:
        while True:
            # print(image_queue.empty())
            if not image_queue.empty():
                stream_type, img = image_queue.get()
                _, buffer = cv2.imencode('.jpg', img)
                message = (stream_type + ':').encode() + buffer.tobytes()
                await websocket.send(message)
                print(f"Sent {stream_type} image of size {len(buffer.tobytes())} bytes")
            # print(diagnostics_queue.empty())
            if not diagnostics_queue.empty():
                diagnostics_message = diagnostics_queue.get()
                await websocket.send(json.dumps({'type': 'diagnostics', 'data': diagnostics_message}))
                print(f"Sending diagnostics data: [{diagnostics_message}]")

            await asyncio.sleep(0.01)  # Relax the loop when the queue is empty.
    except websockets.exceptions.ConnectionClosed as e:
        print(f'WebSocket connection closed: {e}')

# Function to receive and print GPS data
def receive_gps():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('', GPS_PORT))
        print(f"Listening for GPS data on port {GPS_PORT}...")
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            print(f"Received GPS data: {data.decode()} from {addr}")

def receive_diagnostics():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('', DIAGNOSTIC_PORT))
        print(f"Listening for diagnostics on port {DIAGNOSTIC_PORT}...")
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            diagnostics_message = data.decode()
            diagnostics_queue.put(diagnostics_message)
            print(f"Received diagnostics data:[{diagnostics_message}]")

# Main function
def main():
    # Start the threads for video and GPS data reception
    threading.Thread(target=receive_gps, daemon=True).start()
    threading.Thread(target=receive_camera_video, daemon=True).start()
    threading.Thread(target=receive_radar_video, daemon=True).start()
    threading.Thread(target=receive_slam_video, daemon=True).start()
    threading.Thread(target=receive_diagnostics, daemon=True).start()
    
    # Start WebSocket server
    start_server = websockets.serve(send_data, 'localhost', 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
