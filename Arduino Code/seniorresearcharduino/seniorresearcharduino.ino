#include <Stepper.h>
#include <stdlib.h>
/*
 * TO DO:
 * NOTE: The script is chill enough (for now) that we can handle around 5000 steps in .25s, so that allows for full speed of all motors (assuming we have 6) for 800 steps per .25s
 */

int stepperPins[3][2][4] = {{{22, 23, 24, 25}, {26, 27, 28, 29}}, 
                            {{30, 31, 32, 33}, {34, 35, 36, 37}},
                            {{42, 43, 44, 45}, {46, 47, 48, 49}}};

int deltaTime = 1000; //in milliseconds
int deltaOne = 0;

bool stringComplete = false;
int stepperCounter[3][2] = {{0, 800}, {0, 0}, {0, 0}};
int stepperPos[3][2] = {{0, 0}, {0, 0}, {0, 0}};
float stepInterval[3][2] = {{0, 0}, {0, 0}, {0, 0}};
int intervalCounter[3][2] = {{0, 0}, {0, 0}, {0, 0}};
String inputString = "";
String delimiter = ",";
int dutyOn = 500;
int dutyOff = 10;

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
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 2; j++) {
      for (int k = 0; k < 4; k++) {
        pinMode(stepperPins[i][j][k], OUTPUT);
      }
    }
  }
  Serial.begin(250000);
  Serial.println("starting");
  pinMode(LED_BUILTIN, OUTPUT);
  delay(2000);

  //reset all the intervalCounters
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 2; j++) {
      intervalCounter[i][j] = 0;
    }
  }

  //at this point we've gotten new data, now scale the time we have to wait:
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 2; j++) {
      stepInterval[i][j] = float(deltaTime)/float(stepperCounter[i][j]); //figure out how many milliseconds per step
    }
  }

  deltaOne = millis();
  Serial.println(stepInterval[0][1]);
}

void loop() {

  if (Serial.available() > 0) {
    digitalWrite(LED_BUILTIN, HIGH);
    serialEvent();
  }

  if (stringComplete) {
    deltaTime = millis() - deltaOne; //this is how long it took between the last two transactions
    
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

    //reset all the intervalCounters
    for (int i = 0; i < 3; i++) {
      for (int j = 0; j < 2; j++) {
        intervalCounter[i][j] = 0;
      }
    }

    //at this point we've gotten new data, now scale the time we have to wait:
    for (int i = 0; i < 3; i++) {
      for (int j = 0; j < 2; j++) {
        if (stepperCounter[i][j] != 0){
          stepInterval[i][j] = deltaTime/stepperCounter[i][j]; //figure out how many milliseconds per step
        } else {
          stepInterval[i][j] = 1000000000;
        }
      }
    }
    

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
  /*if (millis()%1000 < 1 and counter > 0) {
    char holder [33];
    itoa(stepperCounter[0][0], holder, 10);
    Serial.write(holder);
    Serial.write(" ");
    itoa(stepperCounter[0][1], holder, 10);
    Serial.write(holder);
    Serial.write('\n');
  }*/
  
  //Serial.println("------------------------------");
  //Serial.println(stepperCounter[0][0]);
  //Serial.println(stepperCounter[0][1]);
  //Serial.println(stepperCounter[1][0]);
  //Serial.println(stepperCounter[1][1]);
  //Serial.println(stepperCounter[2][0]);
  //Serial.println(stepperCounter[2][1]);
  //Serial.println(millis());
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
  
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 2; j++) {


      if (stepperCounter[i][j] != 0 and (millis() - deltaOne) > stepInterval[i][j]*(intervalCounter[i][j]-1) + 2 ) { //.5microsec being the minimum time we need on for step to happen
        //minus one on intervalCounter cause we just increased it
        digitalWrite(stepperPins[i][j][0], LOW); //ALL LOW
        digitalWrite(stepperPins[i][j][1], LOW);
        digitalWrite(stepperPins[i][j][2], LOW);
        digitalWrite(stepperPins[i][j][3], LOW);
        
      } else if (stepperCounter[i][j] != 0 and (millis() - deltaOne) > stepInterval[i][j]*intervalCounter[i][j]) { //if it's time to step once:
        intervalCounter[i][j]++; //increment the counter to move it up
        
        if ((stepperCounter[i][j] % 4 + 4) % 4 == 1) {
          digitalWrite(stepperPins[i][j][0], HIGH); //HIGH
          digitalWrite(stepperPins[i][j][1], LOW);
          digitalWrite(stepperPins[i][j][2], HIGH);
          digitalWrite(stepperPins[i][j][3], LOW);

        } else if ((stepperCounter[i][j] % 4 + 4) % 4 == 2) {
          digitalWrite(stepperPins[i][j][0], LOW);
          digitalWrite(stepperPins[i][j][1], HIGH); //HIGH
          digitalWrite(stepperPins[i][j][2], HIGH);
          digitalWrite(stepperPins[i][j][3], LOW);

        } else if ((stepperCounter[i][j] % 4 + 4) % 4 == 3) {
          digitalWrite(stepperPins[i][j][0], LOW);
          digitalWrite(stepperPins[i][j][1], HIGH);
          digitalWrite(stepperPins[i][j][2], LOW); //HIGH
          digitalWrite(stepperPins[i][j][3], HIGH);

        } else {
          digitalWrite(stepperPins[i][j][0], HIGH);
          digitalWrite(stepperPins[i][j][1], LOW);
          digitalWrite(stepperPins[i][j][2], LOW);
          digitalWrite(stepperPins[i][j][3], HIGH); //HIGH
        }      
        if (stepperCounter[i][j] < 0) {
          stepperCounter[i][j]++;
          stepperPos[i][j]--;
        }
        if (stepperCounter[i][j] > 0) {
          stepperCounter[i][j]--;
          stepperPos[i][j]++;
        }
      }
    }  
  }
}

void fastDigitalWrite(int pin, int state) {
  if (pin < 30) {
    if (state == 1) {
      PORTA |= 1 << (pin-22)
    } else {
      PORTA &= ~(1 << (pin-22))
    }
  }

  else if (pin < 40) {
    if (state == 1) {
      PORTC |= 1 << (pin-30)
    } else {
      PORTC &= ~(1 << (pin-30))
    }
  }

  else {
    if (state == 1) {
      PORTL |= 1 << (pin-42)
    } else {
      PORTL &= ~(1 << (pin-42))
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
