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
int stepperPos[3][2] = {{0, 0}, {0, 0}, {0, 0}};
String inputString = "";
String delimiter = ",";
int dutyOn = 500;
int dutyOff = 10;

int waitTime = 100;

float lastStepMillis = 0;

int specialNumber = 123456789;
int linSteps = 0;
int rotSteps = 0;
int writeCounter = 0;
int counter = 0;
int rotCheckLim = 5;
int pos;

unsigned long currentMillis = millis();
unsigned long lastMillis = 0;

void setup() {
  Serial.begin(250000);
  Serial.println("starting");
  pinMode(LED_BUILTIN, OUTPUT);
  delay(2000);
}

void loop() {

  if (Serial.available() > 0) {
    digitalWrite(LED_BUILTIN, HIGH);
    serialEvent();
  }

  if (stringComplete) {
    digitalWrite(LED_BUILTIN, HIGH);
    int writeCounter = 0;
    while((pos = inputString.indexOf(delimiter)) != -1) { //going to be of form val, val, val, ... , val,
      stepperCounter[writeCounter/2][writeCounter%2] = inputString.substring(0, pos).toFloat();
      inputString.remove(0, pos+1);
      writeCounter++;
    }

    //Serial.println("input recieved");
    //Serial.println(stepperCounter[0][0]);
    //Serial.println(stepperCounter[0][1]);
    //Serial.println(stepperCounter[1][0]);
    //Serial.println(stepperCounter[1][1]);
    //Serial.println(stepperCounter[2][0]);
    //Serial.println(stepperCounter[2][1]);
    //Serial.print("at counter ");
    //Serial.println(counter);
    
    counter++;
    Serial.write(counter);
    Serial.write('\n');
    if (counter >= rotCheckLim) { //basically a short clock
      Serial.println("returning the rotation values");
      //less complicated
      for (int i = 0; i < 3; i++) {
        Serial.println(stepperPos[i][1]); //writes all 3 on different lines
        Serial.write(stepperPos[i][1]); //writes all 3 on different lines
        Serial.write('\n');
      }
      Serial.write(specialNumber);
      Serial.write('\n');
      Serial.println("returning to normal stuff now");
      counter = 0;
    }
    
    inputString = "";
    stringComplete = false;
  }
  MoveSteppers(); //actually move the steppers
  //Serial.println("------------------------------");
  //Serial.println(stepperCounter[0][0]);
  //Serial.println(stepperCounter[0][1]);
  //Serial.println(stepperCounter[1][0]);
  //Serial.println(stepperCounter[1][1]);
  //Serial.println(stepperCounter[2][0]);
  //Serial.println(stepperCounter[2][1]);
  Serial.println(millis());
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

void MoveSteppers() {
  if (millis() == lastMillis) {
    return;
  }
  lastMillis = millis();
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 2; j++) {      
      if (stepperCounter[i][j] != 0) {
        //Serial.println(millis());
        if (stepperCounter[i][j] % 4 == 1) {
          digitalWrite(stepperPins[i][j][0], HIGH); //HIGH
          digitalWrite(stepperPins[i][j][1], LOW);
          digitalWrite(stepperPins[i][j][2], HIGH);
          digitalWrite(stepperPins[i][j][3], LOW);
          //delayMicroseconds(dutyOn);
          //digitalWrite(stepperPins[i][j][0], LOW); //ALL LOW
          //digitalWrite(stepperPins[i][j][1], LOW);
          //digitalWrite(stepperPins[i][j][2], LOW);
          //digitalWrite(stepperPins[i][j][3], LOW);
          //delayMicroseconds(dutyOff);
        } else if (stepperCounter[i][j] % 4 == 2) {
          digitalWrite(stepperPins[i][j][0], LOW);
          digitalWrite(stepperPins[i][j][1], HIGH); //HIGH
          digitalWrite(stepperPins[i][j][2], HIGH);
          digitalWrite(stepperPins[i][j][3], LOW);
          //delayMicroseconds(dutyOn);
          //digitalWrite(stepperPins[i][j][0], LOW); //ALL LOW
          //digitalWrite(stepperPins[i][j][1], LOW);
          //digitalWrite(stepperPins[i][j][2], LOW);
          //digitalWrite(stepperPins[i][j][3], LOW);
          //delayMicroseconds(dutyOff);
        } else if (stepperCounter[i][j] % 4 == 3) {
          digitalWrite(stepperPins[i][j][0], LOW);
          digitalWrite(stepperPins[i][j][1], HIGH);
          digitalWrite(stepperPins[i][j][2], LOW); //HIGH
          digitalWrite(stepperPins[i][j][3], HIGH);
          //delayMicroseconds(dutyOn);
          //digitalWrite(stepperPins[i][j][0], LOW); //ALL LOW
          //digitalWrite(stepperPins[i][j][1], LOW);
          //digitalWrite(stepperPins[i][j][2], LOW);
          //digitalWrite(stepperPins[i][j][3], LOW);
          //delayMicroseconds(dutyOff);
        } else {
          digitalWrite(stepperPins[i][j][0], HIGH);
          digitalWrite(stepperPins[i][j][1], LOW);
          digitalWrite(stepperPins[i][j][2], LOW);
          digitalWrite(stepperPins[i][j][3], HIGH); //HIGH
          //delayMicroseconds(dutyOn);
          //digitalWrite(stepperPins[i][j][0], LOW); //ALL LOW
          //digitalWrite(stepperPins[i][j][1], LOW);
          //digitalWrite(stepperPins[i][j][2], LOW);
          //digitalWrite(stepperPins[i][j][3], LOW);
          //delayMicroseconds(dutyOff);
        }      
        if (stepperCounter[i][j] < 0) {
          stepperCounter[i][j]++;
          stepperPos[i][j]--;
        }
        if (stepperCounter[i][j] > 0) {
          stepperCounter[i][j]--;
          stepperPos[i][j]++;
        }
      } else {
      digitalWrite(stepperPins[i][j][0], LOW); //ALL LOW
      digitalWrite(stepperPins[i][j][1], LOW);
      digitalWrite(stepperPins[i][j][2], LOW);
      digitalWrite(stepperPins[i][j][3], LOW);
      delayMicroseconds(dutyOff);  
      } 
    }

    
  }
}


//overly complicated, don't use unless necessary
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
