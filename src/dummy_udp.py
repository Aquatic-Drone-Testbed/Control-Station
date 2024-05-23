import socket
import time
import cv2
import threading

VIDEO_PORT = 9002
BUFFER_SIZE = 65535  # Maximum buffer size for UDP
DIAGNOSTIC_PORT = 20000
SERVER_IP = '127.0.0.1'  # Change this to the IP address of your server if different
SLEEP_TIME = 0.5

def send_diagnostics():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        while True:
            # Send "Camera On" message
            message = b"Camera: On"
            sock.sendto(message, (SERVER_IP, DIAGNOSTIC_PORT))
            print(f"Sent message: {message}")
            time.sleep(SLEEP_TIME)
            message = b"Camera: Off"
            sock.sendto(message, (SERVER_IP, DIAGNOSTIC_PORT))
            print(f"Sent message: {message}")
            time.sleep(SLEEP_TIME)

            message = b"GPS: Has Fix"
            sock.sendto(message, (SERVER_IP, DIAGNOSTIC_PORT))
            print(f"Sent message: {message}")
            time.sleep(SLEEP_TIME)
            message = b"GPS: No Fix"
            sock.sendto(message, (SERVER_IP, DIAGNOSTIC_PORT))
            print(f"Sent message: {message}")
            time.sleep(SLEEP_TIME)

            message = b"Radar: Scanning"
            sock.sendto(message, (SERVER_IP, DIAGNOSTIC_PORT))
            print(f"Sent message: {message}")
            time.sleep(SLEEP_TIME)
            message = b"Radar: Standby"
            sock.sendto(message, (SERVER_IP, DIAGNOSTIC_PORT))
            print(f"Sent message: {message}")
            time.sleep(SLEEP_TIME)

def send_video():
    cap = cv2.VideoCapture(2) 
    if not cap.isOpened():
        print("Error: Could not open the camera.")
        return

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                continue


            # Encode the frame as a JPEG image with reduced quality
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]  # Set JPEG quality to 50
            _, buffer = cv2.imencode('.jpg', frame, encode_param)
            data = buffer.tobytes()

            # Split the data into chunks
            for i in range(0, len(data), BUFFER_SIZE):
                chunk = data[i:i+BUFFER_SIZE]
                sock.sendto(chunk, (SERVER_IP, VIDEO_PORT))
                print(f"Sent chunk of size {len(chunk)} bytes")


if __name__ == "__main__":
    # Create threads for sending dummy data and video
    diagnostic_thread = threading.Thread(target=send_diagnostics)
    video_thread = threading.Thread(target=send_video)

    # Start the threads
    diagnostic_thread.start()
    video_thread.start()

    # Join the threads to ensure they run concurrently
    diagnostic_thread.join()
    video_thread.join()