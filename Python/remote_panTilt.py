"""
V 1.0.4
"""

#TODO: 
# - forhindre at det kommer opp et tomt vindu til å begynne med

import vidTransfer as v
import GUIopenCv as G
import joyinput as j
import cv2
import traceback #gir info om feilmeldinger

client = v.VideoClient(clientAddress="192.168.10.100", port="1234")

runProgram = True #Variabel for om programmet skal kjøre, avbrytes med exit_button
send_joyData = True #Variabel for om data fra joy skal sendes, kan ikke sende joydata samtidig med at annen data som "h" og "a" sendes, greit å kunne skru av joy også (?)
last_button = last_data = None #Må lager en verdi for dette så den ikke aktiverer og deaktiverer knappen mange ganger i sekundet
value_factors = [0.1, 0.5, 1]
value_index = 2 #faktor for hvor mye verdien fra joy skal ganges med

def buttonActions(x = None, y = None, button = None):
    global runProgram, send_joyData, value_index
    if exit_button.isClicked((x,y)) or button == "BACK":
        joy_button.active = False
        runProgram = False
    elif joy_button.isClicked((x, y)) or button == "X":
        joy_button.active = not joy_button.active
        if joy_button.active == False:
            client.sendData("0,0,0,0")
        align_button.deactivate()
        home_button.deactivate()
    elif enable_button.isClicked((x, y)) or button == "B":
        enable_button.active = not enable_button.active
        if enable_button.active:
            client.sendData("e")
        else:
            client.sendData("d")
        align_button.deactivate()
        home_button.deactivate()
    elif home_button.isClicked((x,y)) or button == "Y":
        home_button.active = not home_button.active
        if home_button.active:
            client.sendData("h") 
        align_button.deactivate()
        home_button.deactivate()
    elif align_button.isClicked((x,y)) or button == "A":
        align_button.active = not align_button.active
        if align_button.active:
            client.sendData("a")
        align_button.deactivate()
        home_button.deactivate()
    elif increase_button.isClicked((x,y)) or button == "UP":
        if (value_index < len(value_factors)-1):
            value_index += 1
    elif decrease_button.isClicked((x,y)) or button == "DOWN":
        if (value_index >= 1):
            value_index -= 1
    
def onMouse(event, mouse_x, mouse_y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        buttonActions(x=mouse_x, y=mouse_y)
        distanceToPoint = main.createPoint(mouse_x, mouse_y)
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
main.addObjects([enable_button, home_button, align_button, joy_button, increase_button, decrease_button, exit_button])
main.createBorder()
try:
    while runProgram:
        frame = client.grabFrame()
        main.show(frame, value_factors[value_index])   #tar seg av "q"

        clicked_button = joy.getButton()
        if (clicked_button != last_button):
            last_button = clicked_button
            buttonActions(button=clicked_button)  #sjekk om det er blitt klikket med kontrolleren

        if joy_button.active:
            data = f"{joy.getPosition(0, value_factors[value_index])}, {joy.getPosition(1, value_factors[value_index])}"
            if (data != last_data):
                client.sendData(data)
            last_data = data
except:
    traceback.print_exc()
finally:
    client.stop()   #Tar seg av å sende "s"
    main.destroy()