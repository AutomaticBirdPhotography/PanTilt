import pygame
import time

# Liste over navnene på alle knappene på kontrolleren
BUTTON_NAMES = ['X', 'A', 'B', 'Y', 'BACK', 'UP', 'DOWN']

class Controller:
    def __init__(self, index: int = 0):
        """
        Oppretter en kontroller med angitt indeksnummer `index` (default 0).
        """
        self.index = index
        self.is_disconnected = False
        # Dictionary som holder oversikt over hvilke knapper som er aktive
        # (True) eller ikke (False)
        self.active_buttons = {button: False for button in BUTTON_NAMES}
        self.joystick = None
        # Initialiserer kontrolleren
        self.check_controller()

    def check_controller(self):
        """
        Sjekker om en kontroller er tilkoblet. Hvis en kontroller blir
        tilkoblet, lagrer den referansen til den i `self.joystick`.
        """
        pygame.joystick.init()
        while True:
            joystick_count = pygame.joystick.get_count()
            if joystick_count > 0:
                self.joystick = pygame.joystick.Joystick(self.index)
                self.joystick.init()
                print(f"Kontroller [{+self.joystick.get_name()}] ble koblet til")
                self.is_disconnected = False
                break
            else:
                # Hvis ingen kontroller er tilkoblet, venter den i ett sekund
                # og skriver ut en melding hvis det ikke allerede er gjort
                if not self.is_disconnected:
                    print("Koble til kontroller!")
                    self.is_disconnected = True
                time.sleep(1)

    def get_joystick_position(self, knob_number: int = 0, value_factor: float = 1) -> str:
        """
        Returnerer posisjonen til en joystick-knott i formatet `x,y` som en
        streng. `knob_number` angir hvilken knott som skal avleses (default 0).
        Verdien som returneres er i området -100 til 100, multiplisert med
        `value_factor`.
        """
        try:
            x = round(self.apply_deadzone(self.joystick.get_axis((knob_number+1)*2-2)*100)*value_factor)
            y = round(self.apply_deadzone(self.joystick.get_axis((knob_number+1)*2-1)*100)*value_factor)
            return f"{x:03d},{y:03d}"
        except AttributeError:
            # Hvis kontrolleren ikke er tilgjengelig, skriver den ut en melding
            print("Kontrolleren er ikke tilgjengelig")
            return None

    def get_active_button(self):
        """
        Returnerer navnet på knappen som er aktiv
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
        for i in range(4):
            if (self.joystick.get_button(i) == 1):
                return BUTTON_NAMES[i]
        if (self.joystick.get_button(8) == 1):
            return BUTTON_NAMES[4]
        hat = self.joystick.get_hat(0)[1]
        if hat == 1: return BUTTON_NAMES[5]
        elif hat == -1: return BUTTON_NAMES[6]
        return None

    def toggle_button(self, button_index):
        """
        Bytter tilstanden til en knapp med angitt indeksnummer `button_index`.
        Returnerer navnet på knappen som ble endret.
        """
        button_name = BUTTON_NAMES[button_index]
        self.active_buttons[button_name] = not self.active_buttons[button_name]
        return button_name
    
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

    def stop(self):
        pygame.quit()

    def __del__(self):
        pygame.quit()