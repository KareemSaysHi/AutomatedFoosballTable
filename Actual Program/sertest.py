import serial
import time

ser = serial.Serial('/dev/ttyACM0', 250000, timeout=5)

while True:
    startTime = time.time()
    sendStr = "0,0,0,5,0,0,\n"
    sendStr = bytes(sendStr, 'utf-8')
    ser.write(sendStr) #send to arduino

    if (ser.in_waiting > 0):
        print("line recieved!")
        line = ser.readline()
        print(line.decode('utf-8'))
    while(time.time() - startTime) < 0.1:
        pass
    print(time.time() - startTime)
