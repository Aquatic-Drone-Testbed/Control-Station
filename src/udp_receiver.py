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

# Function to send the video to webGUI using WebSocket
async def send_video(websocket, path):
    print("start send_video()...")
    try:
        while True:
            if not image_queue.empty():
                stream_type, img = image_queue.get()
                _, buffer = cv2.imencode('.jpg', img)
                message = (stream_type + ':').encode() + buffer.tobytes()
                await websocket.send(message)
            else:
                # print("queue is empty")
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

# for test perpose
def display_video():
    cv2.namedWindow("Camera Stream", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Radar Stream", cv2.WINDOW_NORMAL)
    while True:
        if not image_queue.empty():
            stream_type, img = image_queue.get()
            if stream_type == 'camera':
                cv2.imshow('Camera Stream', img)
            elif stream_type == '_radar':
                cv2.imshow('Radar Stream', img)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
                break

    cv2.destroyAllWindows()

def receive_diagnostics():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('', DIAGNOSTIC_PORT))
        print(f"Listening for diagnostics on port {DIAGNOSTIC_PORT}...")
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            print(f"Received  data: {data.decode()} from {addr}")


# if not diagnostics_queue.empty():
#                 diagnostics = diagnostics_queue.get()
#                 diagnostics_message = json.dumps({'type': 'diagnostics', 'data': diagnostics})
#                 print(f"Sending diagnostics message: {diagnostics_message}")  # Log diagnostic data
#                 await websocket.send(diagnostics_message)
            
            # if data == b"GPS Connected":
            #     print(f"GPS is Connected from {addr}")
            #     diagnostics_queue.put({'gps': 'Connected'})
            # if data == b"GPS Not Connected":
            #     print(f"GPS is Not Connected from {addr}")
            #     diagnostics_queue.put({'gps': 'Not Connected'})

# Main function
def main():
    # Start the threads for video and GPS data reception
    threading.Thread(target=receive_gps, daemon=True).start()
    threading.Thread(target=receive_camera_video, daemon=True).start()
    threading.Thread(target=receive_radar_video, daemon=True).start()
    threading.Thread(target=receive_diagnostics, daemon=True).start()
    
    # Start WebSocket server
    start_server = websockets.serve(send_video, 'localhost', 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
    # display_video() # for test perpose, it can only run in main threading

if __name__ == "__main__":
    main()
