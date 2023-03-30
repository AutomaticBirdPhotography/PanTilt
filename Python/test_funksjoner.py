import joyinput as j

joy = j.Controller(1)

while True:
    print(joy.get_active_button())