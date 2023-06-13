import vidTransfer as v
import GUIopenCv as G
import ArduinoSerial as A
import StatusLed as S
from picamera2 import Picamera2
import cv2, traceback, os

log_file = "tripod_error_log.txt" # Fil hvor feilmeldinger lagres
# Empty the log file by opening it in write mode ("w") and truncating its contents
with open(log_file, "w") as f:
    f.truncate()

stream = v.VideoStream(clientAddress="192.168.10.145")
arduino = A.Arduino("/dev/ttyUSB0")

status = S.LEDstatus()
dslr = cv2.VideoCapture(0)
web = Picamera2()
web.configure(web.create_preview_configuration(main={"format": 'XRGB8888', "size": (320, 240)}))
web.start()
status.wait_for_connection()
main = G.window()

previous_data = None
first_run = True
try:
    while True:
            if dslr.isOpened(): #dersom kameraet ikke kunne åpnes vises svart bilde isteden
                _,dslrFrame = dslr.read()
                dslrFrame = G.ensure_valid_frame(dslrFrame)
            else:
                dslrFrame = G.error_window(480, 640, "DSLR connection failed")
            
            try:
                webFrame = web.capture_array()
                webFrame = G.ensure_valid_frame(webFrame)
            except Exception as e:
                print(f"Error capturing image from Picamera2: {str(e)}")
                webFrame = G.error_window(320, 240, "Picamera connection failed")

            data = stream.getData()
            if data is None:
                data = "d"

            #if data != None and len(data) != 0 and data != previous_data:
                #if data[0] == 'r':
                    #fjern r fra strengen, gjør det til liste (ikke streng)
                    #data = eval(data[1:])
                    #print(data)
                    #main.define_roi(data)
            #if main.TRACK(dslrFrame) != None: data = main.TRACK(dslrFrame)
            if data != previous_data and data != None and len(data) > 0:
                if first_run and data != "d":   #data er som standard "d"
                    status.dark()
                    first_run = False
                if data[0] == "p":
                    formatted_data = data[:-1]
                    arduino.send(formatted_data)
                else:
                    arduino.send(data)
                if data == "s":
                    break
            result = G.create_multiple(webFrame, dslrFrame)
            stream.sendFrame(result)

            previous_data = data
except Exception as e:
    status.error()
    traceback.print_exc()
    error_message = "An error occurred: {}\n".format(e)
    traceback_info = traceback.format_exc()
    
    with open(log_file, "a") as f:
        f.write(error_message)
        f.write(traceback_info)
finally:
    print("Avslutter")
    arduino.close()
    status.shut_down()
    main.destroy()
    stream.server.close()
    stream.stop()
    #os.system("sudo shutdown -h now") #skrur av rpi ved stoppkomando/break
