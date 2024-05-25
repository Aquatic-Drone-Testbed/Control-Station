import logging
logging.basicConfig(format='[%(levelname)s] [%(asctime)s] [%(module)s]: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
import socket
import time
import threading
import queue
import asyncio
import websockets

import inputs
import numpy as np
import cv2

class ControlStation:
    REQUEST_CONNECTION_STR = 'Ping'
    ACKNOWLEDGE_CONNECTION_STR = 'Pong'
    # (code, state) -> command
    KEY_TABLE = {
        ('BTN_EAST',  0): 'radar:toggle_scan',
        ('BTN_SOUTH', 0): 'cam:toggle_cam',
        ('BTN_TR',  0): 'radar:zoom_in',
        ('BTN_TL', 0): 'radar:zoom_out',
    }
    LEFT_JOY_CODE = ['ABS_X', 'ABS_Y']
    LEFT_JOY_MAX_VAL = 32768
    RIGHT_JOY_CODE = ['ABS_RX', 'ABS_RY']
    GPS_PORT = 39001
    VIDEO_PORT = 39002
    RADAR_PORT = 39003
    BUFFER_SIZE = 65535


    def __init__(self, usv_ip, usv_port) -> None:
        self.usv_ip = usv_ip
        self.usv_port = usv_port

        self.command_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.command_sock.settimeout(3.0)
        
        self.image_queue = queue.Queue()
        
        self.connect_to_usv()


    def connect_to_usv(self):
        while True:
            logger.info(f'Requesting connection to USV at {self.usv_ip}:{self.usv_port}')
            self.send_to_usv(data=ControlStation.REQUEST_CONNECTION_STR.encode())
            
            try:
                data, server_address = self.command_sock.recvfrom(4096)
            except socket.timeout:
                logger.warning(f'Connection request timed out')
                continue

            if data.decode() == ControlStation.ACKNOWLEDGE_CONNECTION_STR: break

        logger.info(f'Established connection to USV at {self.usv_ip}:{self.usv_port}')
    
    
    def send_controls(self):
        while True:
            event_list = self.get_controller_events()
            if not event_list: continue
            
            command_list = self.get_command_list(event_list)
            for command_str in command_list:
                if not command_str: continue
                self.send_to_usv(data=command_str.encode())
    
    
    def get_controller_events(self) -> str:
        try:
            return inputs.get_gamepad()
        except inputs.UnpluggedError as e:
            logger.error(f'{e}')
            time.sleep(1)
            return
    
    
    def get_command_list(self, event_list: list[inputs.InputEvent]) -> list[str]:
        logger.debug(f'{len(event_list) = }')
        command_list = []
        for event in event_list:
            logger.debug(f'{event.code=}, {event.device=}, {event.ev_type=}, {event.state=}, {event.timestamp=}')
            command = self.get_command_from_event(
                ev_type=event.ev_type,
                code=event.code,
                state=event.state)
            command_list.append(command)
        
        logger.debug(f'{command_list = }')
        return command_list
    
    
    def get_command_from_event(self, ev_type, code, state):
        if ev_type == 'Key':
            return ControlStation.KEY_TABLE.get((code, state), None)
        elif ev_type == 'Absolute':
            if code == 'ABS_Y': state = -state # joystick in vertical direcction is inverted for some reason
            magnitude = state/ControlStation.LEFT_JOY_MAX_VAL
            return f'ctrl:{code},{magnitude}'
        else:
            return None
    
    
    def send_to_usv(self, data: bytes):
        num_bytes_sent = self.command_sock.sendto(data, (self.usv_ip, self.usv_port))
        logger.debug(f'sent ({num_bytes_sent} bytes) to {self.usv_ip}:{self.usv_port}')
    
    
    # Function to receive and decode video data from boat
    def receive_camera_video(self):   
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(('', ControlStation.VIDEO_PORT))
            logger.info(f"Listening for video on port {ControlStation.VIDEO_PORT}...")
            while True:
                data, addr = sock.recvfrom(ControlStation.BUFFER_SIZE)
                logger.debug(f"Received video packet from {addr}, {len(data)} bytes")
                img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
                if img is not None:
                    # Put the image into the queue instead of displaying it directly
                    self.image_queue.put(('camera', img))
                else:
                    logger.error("Could not decode video data")
    
    
    # Function to receive and print GPS data
    def receive_gps(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(('', ControlStation.GPS_PORT))
            logger.info(f"Listening for GPS data on port {ControlStation.GPS_PORT}...")
            while True:
                data, addr = sock.recvfrom(ControlStation.BUFFER_SIZE)
                logger.debug(f"Received GPS data: {data.decode()} from {addr}")
    
    
    def receive_radar_video(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(('', ControlStation.RADAR_PORT))
            logger.info(f"Listening for radar on port {ControlStation.RADAR_PORT}...")
            while True:
                data, addr = sock.recvfrom(ControlStation.BUFFER_SIZE)
                logger.debug(f"Received radar packet from {addr}, {len(data)} bytes")
                img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
                if img is not None:
                    self.image_queue.put(('_radar', img))
                else:
                    logger.error("Could not decode radar data")
    
    
    # for test perpose
    def display_video(self):
        cv2.namedWindow("Camera Stream", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Radar Stream", cv2.WINDOW_NORMAL)
        while True:
            if not self.image_queue.empty():
                stream_type, img = self.image_queue.get()
                if stream_type == 'camera':
                    cv2.imshow('Camera Stream', img)
                elif stream_type == '_radar':
                    cv2.imshow('Radar Stream', img)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
                    break

        cv2.destroyAllWindows()
        
        
    # Function to send the video to webGUI using WebSocket
    async def send_video(self, websocket, path):
        logger.info("start send_video()...")
        try:
            while True:
                if not self.image_queue.empty():
                    stream_type, img = self.image_queue.get()
                    _, buffer = cv2.imencode('.jpg', img)
                    message = (stream_type + ':').encode() + buffer.tobytes()
                    logger.debug(f'sending message: {message}\n')
                    await websocket.send(message)
                else:
                    logger.error("queue is empty")
                    await asyncio.sleep(0.1)  # Relax the loop when the queue is empty.
        except websockets.exceptions.ConnectionClosed as e:
            logger.info(f'WebSocket connection closed: {e}')


def main():
    ctrl_station = ControlStation(usv_ip='192.168.0.111', usv_port=39000)
    # Start the thread for controller
    threading.Thread(target=ctrl_station.send_controls, daemon=True).start()
    
    # Start the threads for video and GPS data reception
    threading.Thread(target=ctrl_station.receive_camera_video, daemon=True).start()
    threading.Thread(target=ctrl_station.receive_gps, daemon=True).start()
    threading.Thread(target=ctrl_station.receive_radar_video, daemon=True).start()
    
    # Start WebSocket server
    webserver = websockets.serve(ctrl_station.send_video, 'localhost', 8765)
    asyncio.get_event_loop().run_until_complete(webserver)
    asyncio.get_event_loop().run_forever() # keep this process alive


if __name__ == '__main__':
    main()
