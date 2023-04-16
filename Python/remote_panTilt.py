#TODO: 
# - vindu skal komme opp med en gang med info om lasting av program
# - fixed aspect ratio på vinduet som kommer opp

import vidTransfer as v
import GUIopenCv as G
import joyinput as j
import cv2
import traceback #gir info om feilmeldinger

client = v.VideoClient()

run_program = True #Variabel for om programmet skal kjøre, avbrytes med exit_button
send_joyData = True #Variabel for om data fra joy skal sendes, kan ikke sende joydata samtidig med at annen data som "h" og "a" sendes, greit å kunne skru av joy også (?)
last_button = last_data = None #Må lager en verdi for dette så den ikke aktiverer og deaktiverer knappen mange ganger i sekundet
value_factors = [0.1, 0.5, 1]
value_index = 1 #faktor for hvor mye verdien fra joy skal ganges med

def buttonActions(x=None, y=None, button=None):
    global run_program, send_joyData, value_index
    
    if exit_button.is_clicked((x,y)) or button == "BACK":
        joy_button.deactivate()
        run_program = False

    elif joy_button.is_clicked((x, y)) or button == "X":
        joy_button.toggle()
        if not joy_button.active:
            client.sendData("0,0,0,0")

    elif enable_button.is_clicked((x, y)) or button == "B":
        enable_button.toggle()
        if enable_button.active:
            client.sendData("e")
        else:
            client.sendData("d")

    elif home_button.is_clicked((x,y)) or button == "Y":
        home_button.toggle()
        if home_button.active:
            client.sendData("h") 
        home_button.deactivate()

    elif align_button.is_clicked((x,y)) or button == "A":
        align_button.toggle()
        if align_button.active:
            client.sendData("a")
        align_button.deactivate()

    elif increase_button.is_clicked((x,y)) or button == "UP":
        if value_index < len(value_factors) - 1:
            value_index += 1

    elif decrease_button.is_clicked((x,y)) or button == "DOWN":
        if value_index >= 1:
            value_index -= 1
    

def onMouse(event, mouse_x, mouse_y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        main.mouse_x = mouse_x
        main.mouse_y = mouse_y
        buttonActions(x=mouse_x, y=mouse_y)
        distanceToPoint = main.create_point(mouse_x, mouse_y)
        if distanceToPoint is not None:
            client.sendData("p{:.3f},{:.3f}".format(distanceToPoint[0], distanceToPoint[1]))
    

joy = j.Controller(1)


main = G.window("Frame", onMouse)
#main.log("laster")

enable_button = G.button(active_text="ON", deactive_text="OFF", start_point=(50,380), height=70, active_color=(0,255,0), deactive_color=(0,0,255))
home_button = G.button("Hjem", "Hjem", (150, 380), 40, (255, 255, 255), (188,32,12))
align_button = G.button("+", "+", (250, 380), 40, (255, 255, 255), (0,255,12))
joy_button = G.button("Stopp joy", "Joy", (350, 380), 40, (255, 255, 255), (188,32,12))
joy_button.activate()
increase_button = G.button("+","+", (650,380), 30, (100,100,100), (255,255,255))
decrease_button = G.button("-","-", (700,380), 30, (100,100,100), (255,255,255))
exit_button = G.button("X", "X", (750, 380), 40, (255,255,255), (0,0,255))
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
    try:
        client.stop()   #Tar seg av å sende "s"
        main.destroy()
    except:
        traceback.print_exc()
        raise Exception("Alvorlige programfeil oppstod")