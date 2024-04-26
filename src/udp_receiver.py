import socket
import numpy as np
import cv2
import asyncio
import websockets
import threading
import queue

# Constants for easy adjustments
GPS_PORT = 9001
VIDEO_PORT = 9002
RADAR_PORT = 9003
BUFFER_SIZE = 65535

# Create a queue for thread-safe image transfer
image_queue = queue.Queue()

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
                image_queue.put(('radar', img))
            else:
                print("Could not decode radar data")

# Function to send the video to webGUI using WebSocket
async def send_video(websocket, path):
    while True:
        if not image_queue.empty():
            stream_type, img = image_queue.get()
            _, buffer = cv2.imencode('.jpg', img)
            message = (stream_type + ':').encode() + buffer.tobytes()
            await websocket.send(message)
        else:
            await asyncio.sleep(0.01)  # Relax the loop when the queue is empty.

# Function to receive and print GPS data
def receive_gps():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('', GPS_PORT))
        print(f"Listening for GPS data on port {GPS_PORT}...")
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            print(f"Received GPS data: {data.decode()} from {addr}")

# for test perpose, it doesnt work now
# def display_video():
#     while True:
#         if not image_queue.empty():
#             img = image_queue.get()
#             cv2.imshow('UDP Stream', img)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

# Main function
def main():
    # Start the threads for video and GPS data reception
    threading.Thread(target=receive_camera_video, daemon=True).start()
    threading.Thread(target=receive_gps, daemon=True).start()
    threading.Thread(target=receive_radar_video, daemon=True).start()
    # threading.Thread(target=receive_gps, daemon=True).start() # for test perpose, it doesnt work now
    
    # Start WebSocket server
    start_server = websockets.serve(send_video, 'localhost', 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
