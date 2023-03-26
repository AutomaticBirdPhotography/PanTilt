"""
V 1.0.4
"""

#TODO: 
# - fixed aspect ratio

import vidTransfer as v
import GUIopenCv as G
import joyinput as j
import cv2
import traceback #gir info om feilmeldinger

client = v.VideoClient(clientAddress="192.168.10.100", port="1234")

run_program = True #Variabel for om programmet skal kjøre, avbrytes med exit_button
send_joyData = True #Variabel for om data fra joy skal sendes, kan ikke sende joydata samtidig med at annen data som "h" og "a" sendes, greit å kunne skru av joy også (?)
last_button = last_data = None #Må lager en verdi for dette så den ikke aktiverer og deaktiverer knappen mange ganger i sekundet
value_factors = [0.1, 0.5, 1]
value_index = 2 #faktor for hvor mye verdien fra joy skal ganges med


def buttonActions(x=None, y=None, button=None):
    global run_program, send_joyData, value_index
    
    # Check if exit button is clicked or 'BACK' button is pressed
    if exit_button.is_clicked((x,y)) or button == "BACK":
        joy_button.active = False
        run_program = False

    # Check if joy button is clicked or 'X' button is pressed
    elif joy_button.is_clicked((x, y)) or button == "X":
        joy_button.active = not joy_button.active
        if not joy_button.active:
            client.sendData("0,0,0,0")
        align_button.deactivate()
        home_button.deactivate()

    # Check if enable button is clicked or 'B' button is pressed
    elif enable_button.is_clicked((x, y)) or button == "B":
        enable_button.active = not enable_button.active
        if enable_button.active:
            client.sendData("e")
        else:
            client.sendData("d")
        align_button.deactivate()
        home_button.deactivate()

    # Check if home button is clicked or 'Y' button is pressed
    elif home_button.is_clicked((x,y)) or button == "Y":
        home_button.active = not home_button.active
        if home_button.active:
            client.sendData("h") 
        align_button.deactivate()
        home_button.deactivate()

    # Check if align button is clicked or 'A' button is pressed
    elif align_button.is_clicked((x,y)) or button == "A":
        align_button.active = not align_button.active
        if align_button.active:
            client.sendData("a")
        align_button.deactivate()
        home_button.deactivate()

    # Check if increase button is clicked or 'UP' button is pressed
    elif increase_button.is_clicked((x,y)) or button == "UP":
        if value_index < len(value_factors) - 1:
            value_index += 1

    # Check if decrease button is clicked or 'DOWN' button is pressed
    elif decrease_button.is_clicked((x,y)) or button == "DOWN":
        if value_index >= 1:
            value_index -= 1
    

def onMouse(event, mouse_x, mouse_y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        buttonActions(x=mouse_x, y=mouse_y)
        distanceToPoint = main.create_point(mouse_x, mouse_y)
        if distanceToPoint is not None:
            client.sendData("p{:.3f},{:.3f}".format(distanceToPoint[0], distanceToPoint[1]))
    

joy = j.Controller(1)


main = G.window("Frame", onMouse)
enable_button = G.button("ON", "OFF", (50,380), 70, 40, (0, 255, 0), (0,0,255))
home_button = G.button("Hjem", "Hjem", (150, 380), 70, 40, (255, 255, 255), (188,32,12))
align_button = G.button("+", "+", (250, 380), 70, 40, (255, 255, 255), (0,255,12))
joy_button = G.button("Stopp joy", "Joy", (350, 380), 200, 40, (255, 255, 255), (188,32,12))
joy_button.activate()
increase_button = G.button("+","+", (650,380), 30,30, (100,100,100), (255,255,255))
decrease_button = G.button("-","-", (700,380), 30,30, (100,100,100), (255,255,255))
exit_button = G.button("X", "X", (750, 380), 70, 40, (255,255,255), (0,0,255))
main.add_objects([enable_button, home_button, align_button, joy_button, increase_button, decrease_button, exit_button])
main.create_border()
try:
    while run_program:
        frame = client.grabFrame()
        main.show(frame, value_factors[value_index])   #tar seg av "q"

        clicked_button = joy.get_active_button()
        if (clicked_button != last_button):
            last_button = clicked_button
            buttonActions(button=clicked_button)  #sjekk om det er blitt klikket med kontrolleren

        if joy_button.active:
            data = f"{joy.get_joystick_position(0, value_factors[value_index])}, {joy.get_joystick_position(1, value_factors[value_index])}"
            if (data != last_data):
                client.sendData(data)
            last_data = data
except:
    traceback.print_exc()
finally:
    client.stop()   #Tar seg av å sende "s"
    main.destroy()