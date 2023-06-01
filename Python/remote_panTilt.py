import vidTransfer as v
import GUIopenCv as G
import joyinput as j
import cv2
import traceback #gir info om feilmeldinger

client = v.VideoClient()
connected_to_tripod = client.is_connected

run_program = True #Variabel for om programmet skal kjøre, avbrytes med exit_button
send_joyData = True #Variabel for om data fra joy skal sendes, kan ikke sende joydata samtidig med at annen data som "h" og "a" sendes, greit å kunne skru av joy også (?)
last_button = last_data = None #Må lager en verdi for dette så den ikke aktiverer og deaktiverer knappen mange ganger i sekundet
value_factors = [0.1, 0.5, 1]
value_index = 1 #faktor for hvor mye verdien fra joy skal ganges med
init_tracking = False

def buttonActions(x=None, y=None, button=None):
    global run_program, send_joyData, value_index, init_tracking
    
    if exit_button.is_clicked((x,y)) or button == "BACK":
        joy_button.deactivate()
        main.destroy()
        run_program = False
        raise Exception("Program avsluttet av bruker")
        

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
    
    #elif roi_button.is_clicked((x,y)):
        #roi_button.toggle()
        #if roi_button.active:
            #init_tracking = True
        #else:
            #init_tracking = False

    elif increase_button.is_clicked((x,y)) or button == "UP":
        if value_index < len(value_factors) - 1:
            value_index += 1

    elif decrease_button.is_clicked((x,y)) or button == "DOWN":
        if value_index >= 1:
            value_index -= 1
    

previous_distance = None
index = 0

def send_point(distanceToPoint):
    global previous_distance, index
    
    if previous_distance is None or distanceToPoint != previous_distance:
        index = 0
        client.sendData("p{:.3f},{:.3f}{}".format(distanceToPoint[0], distanceToPoint[1], index))
    else:
        index += 1
        client.sendData("p{:.3f},{:.3f}{}".format(distanceToPoint[0], distanceToPoint[1], index))

    previous_distance = distanceToPoint

def onMouse(event, mouse_x, mouse_y, flags, param):
    print(event)
    #if init_tracking:
        #roi = main.draw_roi(event, mouse_x, mouse_y)
        #if roi is not None and len(roi) == 4:
            #client.sendData(f"r{roi}")
    if event == cv2.EVENT_LBUTTONDOWN:
        main.mouse_x = mouse_x
        main.mouse_y = mouse_y
        buttonActions(x=mouse_x, y=mouse_y)
        if not init_tracking:
            distanceToPoint = main.create_point(mouse_x, mouse_y)
            if distanceToPoint is not None:
                send_point(distanceToPoint)
    

joy = j.Controller(0)


main = G.window("Frame", onMouse)

enable_button = G.button(active_text="ON", deactive_text="OFF", start_point=(30,380), height=40, active_color=(0,255,0), deactive_color=(0,0,255))
home_button = G.button("Hjem", "Hjem", (120, 380), 40, (255, 255, 255), (188,32,12))
align_button = G.button("+", "+", (240, 380), 40, (255, 255, 255), (0,255,12))
joy_button = G.button("Stopp joy", "Joy", (300, 380), 40, (255, 255, 255), (188,32,12))
joy_button.activate()
increase_button = G.button("+","+", (470,380), 40, (100,100,100), (255,255,255))
decrease_button = G.button("-","-", (520,380), 40, (100,100,100), (255,255,255))
exit_button = G.button("X", "X", (600, 380), 40, (255,255,255), (0,0,255))
#roi_button = G.button("Stop track", "Track", (450, 380), 40, (0,255,0), (255,255,255))


#main.add_objects([exit_button])
main.add_objects([enable_button, home_button, align_button, joy_button, increase_button, decrease_button, exit_button])
main.create_border()

try:
    while run_program:
        if connected_to_tripod:
            main.add_objects([enable_button, home_button, align_button, joy_button, increase_button, decrease_button, exit_button])

        frame = client.grabFrame()
        main.show(frame, value_factors[value_index])   #tar seg av "q"

        clicked_button = joy.get_active_button()
        if (clicked_button != last_button):
            last_button = clicked_button
            buttonActions(button=clicked_button)  #sjekk om det er blitt klikket med kontrolleren

        if joy_button.active and connected_to_tripod:
            data = f"{joy.get_joystick_position(0, value_factors[value_index])}, {joy.get_joystick_position(1, value_factors[value_index])}"
            if (data != last_data):
                client.sendData(data)
            last_data = data
  
finally:
    traceback.print_exc()
    try:
        main.destroy()
        client.stop()   #Tar seg av å sende "s"
    except:
        traceback.print_exc()
        raise Exception("Alvorlige programfeil oppstod")