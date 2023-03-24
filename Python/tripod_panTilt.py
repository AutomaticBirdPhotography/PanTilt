"""
V 1.0.5
"""

import vidTransfer as v
import GUIopenCv as G
#import ArduinoSerial as A
#import StatusLed as S
#from picamera2 import Picamera2
import cv2
import traceback

#status = S.LEDstatus()
#arduino = A.Arduino("/dev/ttyUSB0")
dslr = cv2.VideoCapture(0)
#web = Picamera2()
#web.configure(web.create_preview_configuration(main={"format": 'XRGB8888', "size": (320, 240)}))
#web.start()
#status.wait_for_connection()
stream = v.VideoStream(clientAddress="192.168.10.184", port="1234")
main = G.window()

previous_data = None
try:
    #status.connected()
    while True:
            _,dslrFrame = dslr.read()
            #webFrame =web.capture_array()
            webFrame = cv2.pyrDown(dslrFrame)
            
            result = main.createMultiple(webFrame, dslrFrame)
            stream.sendFrame(result)
            data = stream.getData()
            if data != previous_data and data != None:
                print(data)
                #arduino.send(data)
                if data == "s":
                    break   
            previous_data = data
except:
    #status.error()
    traceback.print_exc()
finally:
    print("Avslutter")
    stream.stop()
    main.destroy()
    #status.shut_down()
