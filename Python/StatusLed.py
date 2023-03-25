import RPi.GPIO as GPIO
import time, threading

class LEDstatus():
    def __init__(self) -> None:
        """
        Venter på kontroller:           fast blått
        Når kontroller er koblet til:   fast grønt frem til første kommando sendes
        Skrus kontrollert av:           fast rødt
        Error:                          blinkende gult
        """
        GPIO.setmode(GPIO.BCM)  #kan ikke være BOARD; fungerer ikke
        GPIO.setup(13,GPIO.OUT)
        GPIO.setup(19,GPIO.OUT)
        GPIO.setup(12,GPIO.OUT)
        self.RedLed = GPIO.PWM(13, 1000)
        self.BlueLed = GPIO.PWM(19, 1000)
        self.GreenLed = GPIO.PWM(12, 1000)
        self.RedLed.start(0)
        self.BlueLed.start(0)
        self.GreenLed.start(0)
        self.state = "idle"
        self.runThread = True
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()
        

    def run(self):
        while self.runThread:
            if self.state == "wait_for_connection":
                self.wait_for_connection_blink()
            elif self.state == "connected":
                self.connected_blink()
            elif self.state == "dark":
                self.dark_blink()
            elif self.state == "error":
                self.error_blink()
            elif self.state == "shut_down":
                self.runThread = False
            time.sleep(0.1)

    def wait_for_connection_blink(self) -> None:
        self.BlueLed.ChangeDutyCycle(100)

    def connected_blink(self) -> None:
        self.BlueLed.ChangeDutyCycle(0)
        self.GreenLed.ChangeDutyCycle(100)

    def dark_blink(self) -> None:
        self.BlueLed.ChangeDutyCycle(0)
        self.RedLed.ChangeDutyCycle(0)
        self.GreenLed.ChangeDutyCycle(0)

    def error_blink(self):
        self.GreenLed.ChangeDutyCycle(0)
        self.RedLed.ChangeDutyCycle(0)
        for i in range(10):
            t_now = time.time()
            self.GreenLed.ChangeDutyCycle(30)            #grønnt lys er mye sterkere enn rødt
            self.RedLed.ChangeDutyCycle(100)
            while time.time()-1 < t_now:
                pass
            self.GreenLed.ChangeDutyCycle(0)
            self.RedLed.ChangeDutyCycle(0)
            while time.time()-0.2 < t_now+1:
                pass


    def wait_for_connection(self) -> None:
        self.state = "wait_for_connection"

    def connected(self) -> None:
        self.state = "connected"

    def error(self) -> None:
        self.state = "error"

    def dark(self) -> None:
        self.state = "dark"

    def shut_down(self) -> None:
        self.RedLed.ChangeDutyCycle(100)
        time.sleep(2)
        self.BlueLed.ChangeDutyCycle(0)
        self.GreenLed.ChangeDutyCycle(0)
        self.RedLed.ChangeDutyCycle(0)
        self.RedLed.stop()
        self.GreenLed.stop()
        self.BlueLed.stop()
        GPIO.cleanup()
        self.state = "shut_down"

