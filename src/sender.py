import socket
import threading
from threading import Thread
import controller
import time

class ExitSignal:
    def __init__(self):
        self.exit = False

# Assuming modifications in controller.GamepadController to accept and use an instance of GracefulExit
        
exit_signal = ExitSignal()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = 9000
server_address = ('192.168.1.108', port)
ctrl = controller.GamepadController(exit_signal)  # Pass exit_signal to the controller

# Modify the GamepadController to check for exit_signal.exit in its loop

# Create and start the controller thread
controller_thread = Thread(target=ctrl.controller_loop)
controller_thread.start()

lock = threading.Lock()

try:
    while True:
        with lock:
            if ctrl.send_data:
                print(f"sending data: {ctrl.send_data}")
                sent = sock.sendto(ctrl.send_data.encode(), server_address)
                ctrl.send_data = ""  # Clear after sending
except KeyboardInterrupt:
    print("Keyboard interrupt received, exiting...")
    exit_signal.exit = True  # Signal the controller thread to exit
finally:
    print("Closing socket")
    sock.close()
    controller_thread.join()  # Ensure the controller thread is cleanly stopped

    print("Shutdown complete.")
