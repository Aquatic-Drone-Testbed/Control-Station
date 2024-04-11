import socket
import numpy as np
import cv2
import threading
import queue

# Constants for easy adjustments
VIDEO_PORT = 9002
GPS_PORT = 9001
BUFFER_SIZE = 65535

# Create a queue for thread-safe image transfer
image_queue = queue.Queue()

# Function to receive and decode video data
def receive_video():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('', VIDEO_PORT))
        print(f"Listening for video on port {VIDEO_PORT}...")
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            print(f"Received video packet from {addr}, {len(data)} bytes")
            img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            if img is not None:
                # Put the image into the queue instead of displaying it directly
                image_queue.put(img)
            else:
                print("Could not decode video data")

# Function to receive and print GPS data
def receive_gps():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('', GPS_PORT))
        print(f"Listening for GPS data on port {GPS_PORT}...")
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            print(f"Received GPS data: {data.decode()} from {addr}")

# Main function
def main():
    # Start the threads for video and GPS data reception
    threading.Thread(target=receive_video, daemon=True).start()
    threading.Thread(target=receive_gps, daemon=True).start()

    try:
        while True:
            if not image_queue.empty():
                img = image_queue.get()
                cv2.imshow('UDP Stream', img)
                if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
                    break
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        cv2.destroyAllWindows()
        print("Terminated both video and GPS data reception")

if __name__ == "__main__":
    main()
