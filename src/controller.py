import inputs

def main():
    while True:
        events = inputs.get_gamepad()
        inputs = inputs.devices.gamepads

        for event in events:
            if event.ev_type == "Button" and event.code == "BTN_SOUTH" and event.state == 1:
                print("A Button Pressed")

if __name__ == "__main__":
    main()
