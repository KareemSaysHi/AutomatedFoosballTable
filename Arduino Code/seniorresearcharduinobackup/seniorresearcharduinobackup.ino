#include <Stepper.h>
#include <stdlib.h>

int stepperPins[3][2][4] = {{{22, 23, 24, 25}, {26, 27, 28, 29}}, 
                            {{30, 31, 32, 33}, {34, 35, 36, 37}}, 
                            {{42, 43, 44, 45}, {46, 47, 48, 49}}};

bool stringComplete = false;

int stepperCounter[3][2] = {{1000, 0}, {0, 0}, {0, 0}};
int stepperPos[3][2] = {{0, 0}, {0, 0}, {0, 0}};
float stepInterval[3][2] = {{0, 0}, {0, 0}, {0, 0}};
int intervalCounter[3][2] = {{0, 0}, {0, 0}, {0, 0}};


String inputString = "";
String delimiter = ",";

int specialNumber = 123456789;
int linSteps = 0;
int rotSteps = 0;
int writeCounter = 0;
int counter = 0;
int rotCheckLim = 5;
int pos;

int deltaTime = 1000; //in milliseconds
unsigned long deltaOne = 0;

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
  Serial.println(stepInterval[0][0]);

  deltaOne = millis();
  Serial.println("beginning loop");
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


/*if (millis() == lastMillis) {
    return;
  }
  if (millis() < lastMillis+5) {
    for (int i = 0; i < 3; i++) {
      for (int j = 0; j < 2; j++) {
        fastDigitalWrite(stepperPins[i][j][0], LOW); //ALL LOW
        fastDigitalWrite(stepperPins[i][j][1], LOW);
        fastDigitalWrite(stepperPins[i][j][2], LOW);
        fastDigitalWrite(stepperPins[i][j][3], LOW);
      }
    }
    return;
  }
  lastMillis = millis();*/
  
void MoveSteppers() {
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 2; j++) { 
      if (stepperCounter[i][j] != 0) {
        if ((millis()-deltaOne) > intervalCounter[i][j]*stepInterval[i][j]) {  
          intervalCounter[i][j]++;
        
          if ((stepperCounter[i][j] % 4 + 4) % 4 == 0) {
            fastDigitalWrite(stepperPins[i][j][0], HIGH);
            fastDigitalWrite(stepperPins[i][j][1], LOW);
            fastDigitalWrite(stepperPins[i][j][2], LOW);
            fastDigitalWrite(stepperPins[i][j][3], LOW);
            
          } else if ((stepperCounter[i][j] % 4 + 4) % 4 == 1) {
            fastDigitalWrite(stepperPins[i][j][0], LOW);
            fastDigitalWrite(stepperPins[i][j][1], LOW);
            fastDigitalWrite(stepperPins[i][j][2], HIGH);
            fastDigitalWrite(stepperPins[i][j][3], LOW);
            
          } else if ((stepperCounter[i][j] % 4 + 4) % 4 == 2) {
            fastDigitalWrite(stepperPins[i][j][0], LOW);
            fastDigitalWrite(stepperPins[i][j][1], HIGH);
            fastDigitalWrite(stepperPins[i][j][2], LOW);
            fastDigitalWrite(stepperPins[i][j][3], LOW);
            
          } else {
            fastDigitalWrite(stepperPins[i][j][0], LOW);
            fastDigitalWrite(stepperPins[i][j][1], LOW);
            fastDigitalWrite(stepperPins[i][j][2], LOW);
            fastDigitalWrite(stepperPins[i][j][3], HIGH);
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
      } else {
        fastDigitalWrite(stepperPins[i][j][0], LOW);
        fastDigitalWrite(stepperPins[i][j][1], LOW);
        fastDigitalWrite(stepperPins[i][j][2], LOW);
        fastDigitalWrite(stepperPins[i][j][3], LOW);
      }
    }
  } 
  delayMicroseconds(600);

  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 3; j++) {
      fastDigitalWrite(stepperPins[i][j][0], LOW);
      fastDigitalWrite(stepperPins[i][j][1], LOW);
      fastDigitalWrite(stepperPins[i][j][2], LOW);
      fastDigitalWrite(stepperPins[i][j][3], LOW);
    }
  }
  
}


void fastDigitalWrite(int pin, int state) {
  if (pin < 30) {
    if (state == 1) {
      PORTA |= 1 << (pin-22);
    } else {
      PORTA &= ~(1 << (pin-22));
    }
  }

  else if (pin < 40) {
    if (state == 1) {
      PORTC |= 1 << (pin-30);
    } else {
      PORTC &= ~(1 << (pin-30));
    }
  }

  else {
    if (state == 1) {
      PORTL |= 1 << (pin-42);
    } else {
      PORTL &= ~(1 << (pin-42));
    }
  }
}
