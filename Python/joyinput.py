"""
V 1.0.2
"""

import pygame
from time import sleep
pygame.init()

knapper = ['X','A','B','Y','BACK','UP','DOWN']
class Controller():
    def __init__(self, index: int = 0):
        self.index = index
        self.disconnected = False
        self.active_button = {knapper[0] : False, knapper[1] : False, knapper[2] : False,knapper[3] : False,knapper[4] : False, knapper[5] : False,knapper[6] : False}
        self.checkPad()

    def checkPad(self):
        #pygame.joystick.quit()
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()
        if joystick_count > 0:
            self.joystick = pygame.joystick.Joystick(self.index)
            self.joystick.init()
            print("["+self.joystick.get_name()+"]" + " ble koblet til")
        if not joystick_count:
            if not self.disconnected:
                print("Koble til joystick!")
                self.disconnected = True
            sleep(1)
            self.checkPad()
        else:
            self.disconnected = False

        
    
    def getPosition(self, knobNumber: int = 0, valueFactor: float = 1) -> str:
        """Få posisjonen str(x,y) til joystick-knotten definert ved `knobNumber`.
        Returnerer verdier fra -100 til 100 ganget med valueFactor
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
        return("{:03d},{:03d}".format(round(self.deadzone(self.joystick.get_axis((knobNumber+1)*2-2)*100)*valueFactor), round(self.deadzone(self.joystick.get_axis((knobNumber+1)*2-1)*100)*valueFactor))) #har 3 siffer - verdiene blir 001,001
    
    def getButton(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
        for i in range(4):
            if (self.joystick.get_button(i) == 1):
                return knapper[i]
        if (self.joystick.get_button(8) == 1):
            return knapper[4]
        hat = self.joystick.get_hat(0)[1]
        if hat == 1: return knapper[5]
        elif hat == -1: return knapper[6]
        
        return None

    def setButton(self, buttonIndex):
        stage = not self.active_button[knapper[buttonIndex]]
        self.active_button = {knapper[0] : False, knapper[1] : False, knapper[2] : False,knapper[3] : False,knapper[4] : False, knapper[5] : False,knapper[6] : False}
        self.active_button[knapper[buttonIndex]] = stage
        return knapper[buttonIndex]
    
    def deadzone(self, value):
        if value <= -100:
            return -100
        elif value >= 100:
            return 100
        elif abs(value) <= 10:
            return 0
        elif value < 0:
            return -((abs(value) - 10) / 90) * 100
        else:
            return ((abs(value) - 10) / 90) * 100

    def stop(self):
        pygame.quit()

    def __del__(self):
        pygame.quit()