import pygame
import time

BUTTON_NUMBER_NAMES = { 0 : "X", 
                        1 : "A",
                        2 : "B",
                        3 : "Y",
                        8 : "BACK"}
HAT_NUMBER_NAMES = { 1 : "UP",
                    -1 : "DOWN"}

class Controller:
    def __init__(self, index: int = 0):
        """
        Oppretter en kontroller med angitt indeksnummer `index` (default 0).
        """
        pygame.init()
        self.index = index
        self.is_connected = False
        self.joystick = None
        self.connect_controller()

    def connect_controller(self):
        """
        Sjekker om en kontroller er tilkoblet. Hvis en kontroller blir
        tilkoblet, lagrer den referansen til den i `self.joystick`.
        """
        
        pygame.event.pump()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            print("koble til joystick")
            self.joystick = None

        else:
            try:
                self.joystick = pygame.joystick.Joystick(self.index)
                self.joystick.init()
                print(f"Kontroller [{self.joystick.get_name()}] ble koblet til")
                self.is_connected = True
            except pygame.error as e:
                if str(e) == 'Invalid joystick device number':
                    self.is_connected = False
                else: raise e
            

    def get_joystick_position(self, knob_number: int = 0, value_factor: float = 1) -> str:
        """
        Returnerer posisjonen til en joystick-knott i formatet `x,y` som en
        streng. `knob_number` angir hvilken knott som skal avleses (default 0).
        Verdien som returneres er i området -100 til 100, multiplisert med
        `value_factor`.
        """
        self.event_checker()
        try:
            if self.is_connected:
                x = round(self.apply_deadzone(self.joystick.get_axis((knob_number+1)*2-2)*100)*value_factor)
                y = round(self.apply_deadzone(self.joystick.get_axis((knob_number+1)*2-1)*100)*value_factor)
            else:
                self.connect_controller()
                x = 0
                y = 0
            return f"{x:03d},{y:03d}"
        except AttributeError:
            # Hvis kontrolleren ikke er tilgjengelig, skriver den ut en melding
            print("Kontrolleren er ikke tilgjengelig")
            return None

    def get_active_button(self):
        """
        Returnerer navnet på knappen som er aktiv
        """
        self.event_checker()

        if not self.is_connected:
            self.connect_controller() 
            return None

        for i in range(self.joystick.get_numbuttons()):
            if (self.joystick.get_button(i) == 1) and i in BUTTON_NUMBER_NAMES:
                return BUTTON_NUMBER_NAMES[i]

        hat = self.joystick.get_hat(0)[1]
        if hat != 0 and hat in HAT_NUMBER_NAMES:
            return HAT_NUMBER_NAMES[hat]
            
        return None
        

    
    def apply_deadzone(self, value):
        """
        Legger til en dødsone
        """
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
        
    def event_checker(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
            elif event.type == pygame.JOYDEVICEREMOVED:
                self.joystick.quit()
                self.joystick = None
                self.is_connected = False

    def stop(self):
        pygame.quit()

    def __del__(self):
        pygame.quit()