#include <Stepper.h>

/*
 * TO DO:
 * NOTE: The script is chill enough (for now) that we can handle around 5000 steps in .25s, so that allows for full speed of all motors (assuming we have 6) for 800 steps per .25s
 */

int stepperPins[3][2][4] = {{{2, 3, 4, 5}, {6, 7, 8, 9}}, 
                            {{10, 11, 12, 13}, {14, 15, 16, 17}},
                            {{18, 19, 20, 21}, {22, 23, 24, 25}}};

bool stringComplete = false;
float pwmSpeed = 10; //in milliseconds
int stepperCounter[3][2] = {{10000, 10000}, {10000, 10000}, {10000, 10000}};
String inputString = "";
String delimiter = ","

float lastStepMillis = 0;
float deltaTime = 0.002;

int specialNumber = 123456789;
int linSteps = 0;
int rotSteps = 0;
int counter = 0;
int rotCheckLim = 100;


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
    inputString.erase(0, s.find(delimiter, 
    
    float rot = (inputString.substring(linIndex+1, inputString.length()+1)).toFloat();
    
    //Serial.println(lin);
    //Serial.println(rot);

    UpdateCounters(lin1, rot1, lin2, rot2, lin3, rot3);

    counter++;
    if (counter > rotCheckLim) {
      /*char rotToSend[];
      for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 2; h++) {
          int len = to_string(stepperCounter[i][j][1]).length();
          char* nchar = new char[len];
          numberChar = to_chars(nchar, nchar+len, number);
          strcat(rotToSend, numberChar)
          strcat(rotToSend, ';')
        }
        Serial.write(stepperCounter[i][j][1]) //writes all 8
      }*/

      //less complicated
      Serial.write(specialNumber);
      for (int i = 0; i < 3; i++) {
        Serial.write(stepperCounter[i][1]); //writes all 8 on different lines
      }
    }
    
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

void UpdateCounters(float lin1, float lin2, float lin3, float rot) {
  //everything needs to be done on the pi to optimize speed

  //to change speed to steps:
  linSteps = int(lin / 6.28 * 200 * deltaTime); //divide by circumference, multiply by steps, times deltaTime
  rotSteps = int(rot * 200 / 360 * deltaTime); //multiply by steps, divide by degrees, times deltaTime

  stepperCounter[0] = linSteps;
  stepperCounter[1] = rotSteps;
}

void MoveSteppers() {
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 2, j++) {      
        if (stepperCounter[i][j] != 0) {
          //Serial.println(millis());
          if (stepperCounter[i][j] % 4 == 1) {
            digitalWrite(stepperPins[i][j][0], HIGH); //HIGH
            digitalWrite(stepperPins[i][j][1], LOW);
            digitalWrite(stepperPins[i][j][2], LOW);
            digitalWrite(stepperPins[i][j][3], LOW);
          } else if (stepperCounter[i][j] % 4 == 2) {
            digitalWrite(stepperPins[i][j][0], LOW);
            digitalWrite(stepperPins[i][j][1], HIGH); //HIGH
            digitalWrite(stepperPins[i][j][2], LOW);
            digitalWrite(stepperPins[i][j][3], LOW);
          } else if (stepperCounter[i][j] % 4 == 3) {
            digitalWrite(stepperPins[i][j][0], LOW);
            digitalWrite(stepperPins[i][j][1], LOW);
            digitalWrite(stepperPins[i][j][2], HIGH); //HIGH
            digitalWrite(stepperPins[i][j][3], LOW);
          } else {
            digitalWrite(stepperPins[i][j][0], LOW);
            digitalWrite(stepperPins[i][j][1], LOW);
            digitalWrite(stepperPins[i][j][2], LOW);
            digitalWrite(stepperPins[i][j][3], HIGH); //HIGH
          }      
          if (stepperCounter[i] < 0) stepperCounter[i]++;
          if (stepperCounter[i] > 0) stepperCounter[i]--;
        } else {
            Serial.println(millis());
        }
      
    }
  }
}
