import socket
import time

# Constants
DIAGNOSTIC_PORT = 20000
SERVER_IP = '127.0.0.1'  # Change this to the IP address of your server if different

def send_dummy_data():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        while True:
            # Send "Camera On" message
            message = b"Camera: On"
            sock.sendto(message, (SERVER_IP, DIAGNOSTIC_PORT))
            print(f"Sent message: {message}")
            time.sleep(2.5)
            message = b"Camera: Off"
            sock.sendto(message, (SERVER_IP, DIAGNOSTIC_PORT))
            print(f"Sent message: {message}")
            time.sleep(2.5)

            message = b"Camera: On"
            sock.sendto(message, (SERVER_IP, DIAGNOSTIC_PORT))
            print(f"Sent message: {message}")
            time.sleep(2.5)
            message = b"Camera: Off"
            sock.sendto(message, (SERVER_IP, DIAGNOSTIC_PORT))
            print(f"Sent message: {message}")
            time.sleep(2.5)

if __name__ == "__main__":
    send_dummy_data()
