import joyinput as j

joy = j.Controller(1)

while True:
    print(joy.get_joystick_position(0))