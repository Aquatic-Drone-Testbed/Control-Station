# this python script is only for testing perpose.
# we can run this script for generate some fake data from the boat

import socket
import cv2
import numpy as np
import time


def send_video_data(image_path, port, description):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', port)

    frame = cv2.imread(image_path)
    if frame is not None:
        frame = cv2.resize(frame, (320, 240)) 

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 40] 
        _, frame_encoded = cv2.imencode('.jpg', frame, encode_param)
        data = frame_encoded.tobytes()

        print(f"Data size: {len(data)} bytes")

        if len(data) < 65507:
            sock.sendto(data, server_address)
            print(f"Sent {description} data: {len(data)} bytes to port {port}")
        else:
            print("Data packet is too large to send over UDP")
    else:
        print(f"Failed to load image: {image_path}")

    sock.close()

def main(): 
    interval = 1
    
    i = 1
    j = 2
    data_amount = 20 # change this value to the data that you have
    while True:
        
        if i < data_amount: i += 1
        else: i = 1
        if j < data_amount: j += 1
        else: j = 1

        camera_image_path = f'./src/fakeData/{i}.jpg'
        radar_image_path = f'./src/fakeData/{j}.jpg'

        send_video_data(camera_image_path, 9002, 'camera video')

        send_video_data(radar_image_path, 9003, 'radar video')

        time.sleep(interval)

if __name__ == "__main__":
    main()
