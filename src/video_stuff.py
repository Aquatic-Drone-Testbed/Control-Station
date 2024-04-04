import socket
import numpy as np
import subprocess
import cv2

# Constants
IP = '127.0.0.1'
PORT = 9001
BUFFER_SIZE = 65535
FFMPEG_CMD = ['ffmpeg', '-f', 'image2pipe', '-pix_fmt', 'bgr24', '-s', '640x480', '-i', '-', '-f', 'mjpeg', '-q:v', '5', 'http://localhost:8080/feed.ffm']

def pipe_frames_to_ffmpeg(ip=IP, port=PORT, buffer_size=BUFFER_SIZE, ffmpeg_cmd=FFMPEG_CMD):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock, subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE) as ffmpeg:
        sock.bind((ip, port))
        print(f"Listening for UDP packets on {ip}:{port}...")

        try:
            while True:
                data, addr = sock.recvfrom(buffer_size)
                print(f"Received packet from {addr}, {len(data)} bytes")

                img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)

                if img is not None:
                    # Write the frame to FFmpeg's stdin as raw data
                    ffmpeg.stdin.write(img.tobytes())
                    # cv2.imshow('UDP Stream', img)
                    # if cv2.waitKey(1) & 0xFF == ord('q'): # If q is pressed on keyboard
                    #     break
                else:
                    print("Could not decode image data")
        except KeyboardInterrupt:
            print("\nStopped by user")
        finally:
            print("Streaming stopped")

if __name__ == "__main__":
    pipe_frames_to_ffmpeg()
