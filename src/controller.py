import inputs
import time

class GamepadController:
    def __init__(self, exit_signal):
        print(f"TEST {type(exit_signal)}")
        self.send_data = ""
        self.exit_signal = exit_signal  # Correctly receive and store the exit signal
        print("Gamepad Controller initialized. Press CTRL+C to exit. You can disconnect and reconnect the gamepad.")
    
    def get_gamepad_events(self):
        """Attempt to get gamepad events and handle disconnections."""
        try:
            events = inputs.get_gamepad()
            return events
        except inputs.UnpluggedError:  # Correct exception
            return None

    def wait_for_gamepad_reconnection(self):
        """Wait for the gamepad to be reconnected."""
        print("Gamepad controller not found. Please connect a gamepad...")
        events = None
        while not events and not self.exit_signal.exit:  # Corrected to check self.exit_signal.exit
            print("Waiting for gamepad connection...")
            time.sleep(1)  # Wait a bit before trying again to avoid flooding the console
            events = self.get_gamepad_events()
            if self.exit_signal.exit:  # Corrected the check for exit_signal
                return None
        if events:
            print("Gamepad controller connected")
        return events

    def process_event_button(self, event):
        """Process individual gamepad button event."""
        match event.code:
            case "BTN_EAST":
                action = "pressed" if event.state else "released"
                print(f"B (East) Button {action}")
            case "BTN_SOUTH":
                action = "pressed" if event.state else "released"
                print(f"A (South Button) {action}")
            case "BTN_WEST":
                action = "pressed" if event.state else "released"
                print(f"X (West Button) {action}")
            case "BTN_NORTH":
                action = "pressed" if event.state else "released"
                print(f"Y (North Button) {action}")
            case _:
                print(f"Unhandled Event: {event.ev_type}, Code: {event.code}, State: {event.state}")

    def process_event_joystick(self, event):
        """Process individual gamepad joystick event."""
        if event.code in ('ABS_X', 'ABS_Y', "ABS_RX", "ABS_RY"):
            print(f"Joystick Event: {event.ev_type}, Code: {event.code}, State: {event.state}")
            return f"CTRL:{event.code},{event.state}"

    def controller_loop(self):
        print("Main loop entered to process gamepad events.")
        while not self.exit_signal.exit:  # Correctly use the exit signal to control the loop
            events = self.get_gamepad_events()
            if events:
                for event in events:
                    if event.ev_type == 'Key':
                        self.process_event_button(event)
                    elif event.ev_type == "Absolute":
                        self.send_data += self.process_event_joystick(event) + "\n"  # Accumulate data if needed
            else:
                self.wait_for_gamepad_reconnection()
                if self.exit_signal.exit:  # Check the exit signal again after reconnection
                    break
            #time.sleep(0.1)  # Small delay to avoid hogging CPU resources
