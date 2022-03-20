#include <Stepper.h>

/*
 * TO DO:
 * NOTE: The script is chill enough (for now) that we can handle around 5000 steps in .25s, so that allows for full speed of all motors (assuming we have 6) for 800 steps per .25s
 */

int stepperPins[2][4] = {{2, 3, 4, 5}, {6, 7, 8, 9}};

bool stringComplete = false;
float pwmSpeed = 10; //in milliseconds
int stepperCounter[2] = {10000, 10000};
String inputString = "";

float lastStepMillis = 0;
float deltaTime = 0.002;

int linSteps = 0;
int rotSteps = 0;

void setup() {
  Serial.begin(250000);
  Serial.println("starting");
}

void loop() {

  if (Serial.available() > 0) serialEvent();

  unsigned long currentMillis = millis();

  MoveSteppers();
  
  if (stringComplete) {
    int linIndex = inputString.indexOf(",");   //put in x and y vals
    float lin = (inputString.substring(1, linIndex)).toFloat();
    float rot = (inputString.substring(linIndex+1, inputString.length()+1)).toFloat();
    
    //Serial.println(lin);
    //Serial.println(rot);

    UpdateCounters(lin, rot);
    
    inputString = "";
    stringComplete = false;
  }
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}

void UpdateCounters(float lin, float rot) {
  //everything needs to be done on the pi to optimize speed

  //to change speed to steps:
  linSteps = int(lin / 6.28 * 200 * deltaTime); //divide by circumference, multiply by steps, times deltaTime
  rotSteps = int(rot * 200 / 360 * deltaTime); //multiply by steps, divide by degrees, times deltaTime

  stepperCounter[0] = linSteps;
  stepperCounter[1] = rotSteps;
}

void MoveSteppers() {
  for (int i = 0; i < 2; i++) {      
    if (stepperCounter[i] != 0) {
      //Serial.println(millis());
      if (stepperCounter[i] % 4 == 1) {
        digitalWrite(stepperPins[i][0], HIGH); //HIGH
        digitalWrite(stepperPins[i][1], LOW);
        digitalWrite(stepperPins[i][2], LOW);
        digitalWrite(stepperPins[i][3], LOW);
      } else if (stepperCounter[i] % 4 == 2) {
        digitalWrite(stepperPins[i][0], LOW);
        digitalWrite(stepperPins[i][1], HIGH); //HIGH
        digitalWrite(stepperPins[i][2], LOW);
        digitalWrite(stepperPins[i][3], LOW);
      } else if (stepperCounter[i] % 4 == 3) {
        digitalWrite(stepperPins[i][0], LOW);
        digitalWrite(stepperPins[i][1], LOW);
        digitalWrite(stepperPins[i][2], HIGH); //HIGH
        digitalWrite(stepperPins[i][3], LOW);
      } else {
        digitalWrite(stepperPins[i][0], LOW);
        digitalWrite(stepperPins[i][1], LOW);
        digitalWrite(stepperPins[i][2], LOW);
        digitalWrite(stepperPins[i][3], HIGH); //HIGH
      }      
      if (stepperCounter[i] < 0) stepperCounter[i]++;
      if (stepperCounter[i] > 0) stepperCounter[i]--;
    } else {
        Serial.println(millis());
 
    }
  }
}
