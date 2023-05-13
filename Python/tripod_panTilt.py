import vidTransfer as v
import GUIopenCv as G
import ArduinoSerial as A
import StatusLed as S
from picamera2 import Picamera2
import cv2
import traceback
import numpy as np

stream = v.VideoStream(clientAddress="192.168.10.184")
arduino = A.Arduino("/dev/ttyUSB0")

status = S.LEDstatus()
dslr = cv2.VideoCapture(3)
#web = Picamera2()
#web.configure(web.create_preview_configuration(main={"format": 'XRGB8888', "size": (320, 240)}))
#web.start()
status.wait_for_connection()
main = G.window()

previous_data = None
try:
    while True:
            if dslr.isOpened(): #dersom kameraet ikke kunne åpnes vises svart bilde isteden
                _,dslrFrame = dslr.read()
            else:
                dslrFrame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(dslrFrame, "DSLR connection failed", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
            
            try:
                webFrame = web.capture_array()
            except Exception as e:
                print(f"Error capturing image from Picamera2: {str(e)}")
                #webFrame = np.zeros((240, 320, 3), dtype=np.uint8)
                webFrame = G.error_window(240, 320)
                cv2.putText(webFrame, "Picamera connection failed", (5, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

            data = stream.getData()
            #if data != None and len(data) != 0 and data != previous_data:
                #if data[0] == 'r':
                    #fjern r fra strengen, gjør det til liste (ikke streng)
                    #data = eval(data[1:])
                    #print(data)
                    #main.define_roi(data)
            #if main.TRACK(dslrFrame) != None: data = main.TRACK(dslrFrame)
            if data != previous_data and data != None:
                status.dark()
                print(data)
                arduino.send(data)
                if data == "s":
                    break
            result = main.create_multiple(webFrame, dslrFrame)
            stream.sendFrame(result)

            previous_data = data
except:
    status.error()
    traceback.print_exc()
finally:
    print("Avslutter")
    arduino.close()
    status.shut_down()
    main.destroy()
    stream.server.close()
    stream.stop()
