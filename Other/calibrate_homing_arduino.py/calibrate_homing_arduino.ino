#include <AccelStepper.h>
#define motorInterfaceType 1

const int potPin = A7;
const int vertikalDirPin = 7;
const int vertikalStepPin = 6;
const int enablePin = 2;

const int run_steps = 500; // hvor langt motoren skal kjøre til hver side for å lese av pot-verdien
int upValue = 0;            // når den kjører run_steps framover er dette pot-verdien i enden.
int downValue = 0;

AccelStepper vertikal = AccelStepper(motorInterfaceType, vertikalStepPin, vertikalDirPin);

int getPotoentiometerValue(int pin){
    unsigned long potValue = 0;
    for (int i = 0; i < 500; i++){
        potValue += analogRead(pin);
    }
    return potValue / 500;
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("Plasser stativet i hjemposisjon og skriv inn 'y'");
    pinMode(potPin, INPUT);
    vertikal.setMaxSpeed(50);
    vertikal.setCurrentPosition(0);
    vertikal.setAcceleration(10);
    vertikal.setEnablePin(enablePin);
    vertikal.setPinsInverted(false, false, true);
    vertikal.setSpeed(50);
    vertikal.enableOutputs();
}

void loop() {
    if (Serial.available() > 0) {
    char input = Serial.read();
    if (input == 'y') {
        vertikal.enableOutputs();
        vertikal.setCurrentPosition(0);
        Serial.println("Hjemposisjon satt.");
        Serial.println("Kjører kalibreringsprosess ...");
        vertikal.runToNewPosition(run_steps);
        delay(500);
        upValue = getPotoentiometerValue(potPin);
        delay(500);
        vertikal.runToNewPosition(-run_steps);
        delay(500);
        downValue = getPotoentiometerValue(potPin);
        delay(500);
        vertikal.runToNewPosition(0);
        String code = "int absolutePosition = map(potValue, " + String(upValue) + ", " + String(downValue) + ", " + String(run_steps) + ", " + String(-run_steps) + ");";
        Serial.println(code);
        vertikal.disableOutputs();
    }
  }
}