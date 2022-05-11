int pin1a = 22;
int pin1b = 23;
int pin2a = 24;
int pin2b = 25;
int dutyOn = 1000; 
int dutyOff = 2000; //most I can do in terms of power stuff

void setup() {
  // put your setup code here, to run once:
  pinMode(pin1a, OUTPUT);
  pinMode(pin1b, OUTPUT);
  pinMode(pin2a, OUTPUT);
  pinMode(pin2b, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  for (int i = 0; i < 50; i++) {
    digitalWrite(pin1a, HIGH);
    digitalWrite(pin1b, LOW);
    digitalWrite(pin2a, LOW);
    digitalWrite(pin2b, LOW);
  
    delayMicroseconds(dutyOn);

    digitalWrite(pin1a, LOW);
    digitalWrite(pin1b, LOW);
    digitalWrite(pin2a, LOW);
    digitalWrite(pin2b, LOW);
  
    delayMicroseconds(dutyOff);
  
    digitalWrite(pin1a, LOW);
    digitalWrite(pin1b, LOW);
    digitalWrite(pin2a, HIGH);
    digitalWrite(pin2b, LOW);
    
    delayMicroseconds(dutyOn);

    digitalWrite(pin1a, LOW);
    digitalWrite(pin1b, LOW);
    digitalWrite(pin2a, LOW);
    digitalWrite(pin2b, LOW);
  
    delayMicroseconds(dutyOff);
  
    digitalWrite(pin1a, LOW);
    digitalWrite(pin1b, HIGH);
    digitalWrite(pin2a, LOW);
    digitalWrite(pin2b, LOW);
    
    delayMicroseconds(dutyOn);

    digitalWrite(pin1a, LOW);
    digitalWrite(pin1b, LOW);
    digitalWrite(pin2a, LOW);
    digitalWrite(pin2b, LOW);
  
    delayMicroseconds(dutyOff);
  
    digitalWrite(pin1a, LOW);
    digitalWrite(pin1b, LOW);
    digitalWrite(pin2a, LOW);
    digitalWrite(pin2b, HIGH);
    
    delayMicroseconds(dutyOn);

    digitalWrite(pin1a, LOW);
    digitalWrite(pin1b, LOW);
    digitalWrite(pin2a, LOW);
    digitalWrite(pin2b, LOW);
  
    delayMicroseconds(dutyOff);
  }
}

void digitalWrite(int pin, int state) {
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
