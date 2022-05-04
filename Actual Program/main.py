from argon2 import PasswordHasher
import cvmethods
import cv2
import time
import sys
import imutils
import numpy as np
from centroidtracker import CentroidTracker
from onnxhelper import OnnxHelper
import serial
import keyboard

class AutomatedFoosballTable():
    
    def __init__(self):
        
        self.deltaTime = 0.05
        #open serial
        #self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=5) 
        self.specialNumber = 123456789

        #define some standard values:
        self.isPlaying = False
        self.rodPos = [0, 0, 0, 0, 0, 0] #enemy, offense, enemy, mid, enemy, defense
        self.rodRot = [None, 0, None, 0, None, 0]
        self.ballPos = 0
        self.noBallCounter = 0

        self.ct = CentroidTracker()
        
        self.oh = OnnxHelper()

        self.totalStepCounter = 0
        self.readRotCounterLim = 100

        self.cap = cv2.VideoCapture(-1)
            
        self.cap.set(3, 960)
        self.cap.set(4, 540)
      
        #Look for four aruco tags

        while True: 
            ret, frame = self.cap.read()
            frame = self.resize(frame, 50)
            arucos = cvmethods.findAruco(frame)
            cv2.imshow("aruco", frame)
            if arucos[3] == True: #if four have been found
                break
            
            if cv2.waitKey(1) & 0xFF == ord('q'):  
                self.end()
                
                sys.exit("Manually exited the program")
        
        cv2.destroyAllWindows()

        #Find a transformation using the four found arucos

        corners = arucos[1]
        ids = arucos[2]

        pTrans = cvmethods.findPerspectiveTransform(frame, corners, ids)
        
        self.transParams = list(pTrans)

        frame = cvmethods.transformPerspective(frame, *self.transParams)

        cv2.imshow("warped", frame)
        print("press c to continue, and q to quit")
        
        while True:      
            if cv2.waitKey(1) & 0xFF == ord('q'):  
                self.end()
            elif cv2.waitKey(1) & 0xFF == ord('c'):  
                break

        cv2.destroyAllWindows()

        #check ball tracking until continue

        print("looking for ball")
        while True:
            frame = self.newFrame()

            ball, center = cvmethods.getBallPos(frame)
            cv2.imshow("ball tracking", ball)
            
            if cv2.waitKey(1) & 0xFF == ord('c'):  
                break
            elif cv2.waitKey(1) & 0xFF == ord('q'):  
                self.end()
                sys.exit("Manually exited the program")

        cv2.destroyAllWindows()

        #Initialize rod positions

        #Find two rods

        counter = 0
        while True:
            frame = self.newFrame()
            rodPoints, frame = cvmethods.getRodPoints(frame)
            cv2.imshow("frame", frame)
            print("rodpoints then counter twice")
            print(len(rodPoints))
            print(counter)

            if len(rodPoints) == 2: #we found both rods
                counter = counter + 1
            else:
                counter = 0

            print(counter)

            if counter == 3: #for consistency
                break 
            
            if cv2.waitKey(1) & 0xFF == ord('q'):  
                self.end()
                sys.exit("Manually exited the program")

            time.sleep(0.02)
        
        cv2.destroyAllWindows

        #get y coords of rods:
        yArray = ([rodPoints[i][1] for i in range (0, len(rodPoints))])
        ySortArray = np.argsort(yArray)
        sortedRodPoints = ([rodPoints[ySortArray[i]] for i in range (0, len(ySortArray))]) #sorted by y value

        for i in range (0, len(sortedRodPoints)):
            self.ct.register(sortedRodPoints[i], i) #register point with id i (increasing order in y)


    def main(self):
        print("entering main")
        while True:
            self.totalStepCounter += 1 #update counters

            frame = self.newFrame() #make a new frame

            ball, center = cvmethods.getBallPos(frame) #get ball data
            if center == None:  #if it doesn't see the ball, power off
                self.noBallCounter += 1 #ball pos doesn't update if ball not found
                if self.noBallCounter > 200:
                    self.isPlaying = False
            else: 
                self.ballPos = center
                self.noBallCounter = 0
                self.isPlaying = True

            if self.isPlaying: #everything else is contained in this if statement
                
                rodPoints = cvmethods.getRodPoints(frame)[0] #get rod data

                objects = self.ct.update(rodPoints) #and update

                self.rodPos = []
                for i in range(0, len(objects.items())): #each item is (objectId, centroid)
                    print(objects.items())
                    self.rodPos.append([list(objects.items())[i][0]/frame.shape[1]]) #0 for the x value, normalize it

                for (objectId, centroid) in objects.items(): #just for visualization
                    text = "ID {}".format(objectId)
                    cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                linSteps, rotSteps = self.oh.runOnnx(self.ballPos, self.rodPos, self.rodRot) #run onnx
                sendStr = str(linSteps) + "," + str(rotSteps) + ",0,0,0,0,\n" #format
                sendStr = bytes(sendStr, 'utf-8')
                self.ser.write(sendStr) #send to arduino

                if self.totalStepCounter % self.readRotCounterLim == 0: #check if we need to update rotation values
                    if self.ser.in_waiting: #see if serial has stuff in it
                        serLine = int(self.ser.readline().strip('\n')) #format the line
                        if serLine == self.specialNumber: #see if we have terminating number
                            rodMaskArray = [1, 3, 5] 
                            for i in range(0, 3):
                                serLine = int(self.ser.readline().strip('\n'))
                                self.rodRot[rodMaskArray[i]] = self.oh.stepsToRot(serLine) #update the changes

                cv2.imshow("frame", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

    def mainThrees(self):
        print("entering main but for threes")
        while True:
            self.totalStepCounter += 1 #update counters

            frame = self.newFrame() #make a new frame

            center = cvmethods.getBallPos(frame)[1] #get ball data
            if center == None:  #if it doesn't see the ball, power off
                self.noBallCounter += 1 #ball pos doesn't update if ball not found
                if self.noBallCounter > 200:
                    self.isPlaying = False
            else: 
                self.ballPos = center
                self.noBallCounter = 0
                self.isPlaying = True

            if self.isPlaying: #everything else is contained in this if statement
                
                rodPoints = cvmethods.getRodPoints(frame)[0] #get rod data

                objects = self.ct.update(rodPoints) #and update

                self.rodPos = []
                for i in range(0, len(objects.items())): #each item is (objectId, centroid)
                    print(objects.items())
                    self.rodPos.append([list(objects.items())[i][0]/frame.shape[1]]) #0 for the x value, normalize it

                for (objectId, centroid) in objects.items(): #just for visualization
                    text = "ID {}".format(objectId)
                    cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                linoffSteps, linmidSteps, lindefSteps, rotoffSteps, rotmidSteps, rotdefSteps = self.oh.runOnnxThrees(self.ballPos, self.rodPos, self.rodRot) #run onnx

                sendStr = str(linoffSteps) + "," + str(rotoffSteps) + "," + str(linmidSteps) + "," + str(rotmidSteps) + "," + str(lindefSteps) + "," + str(rotdefSteps) + "," + "\n" #format
                sendStr = bytes(sendStr, 'utf-8')
                self.ser.write(sendStr) #send to arduino

                if self.totalStepCounter % self.readRotCounterLim == 0: #check if we need to update rotation values
                    if self.ser.in_waiting: #see if serial has stuff in it
                        serLine = int(self.ser.readline().strip('\n')) #format the line
                        if serLine == self.specialNumber: #see if we have terminating number
                            rodMaskArray = [1, 3, 5] 
                            for i in range(0, 3):
                                serLine = int(self.ser.readline().strip('\n'))
                                self.rodRot[rodMaskArray[i]] = self.oh.stepsToRot(serLine) #update the changes

                cv2.imshow("frame", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

    def keyboardControl(self):
        while True:
            self.totalStepCounter += 1 #update counters
            frame = self.newFrame() #make a new frame
            ball, center = cvmethods.getBallPos(frame) #get ball data
            if center == None:  #if it doesn't see the ball, power off
                self.noBallCounter += 1 #ball pos doesn't update if ball not found
                if self.noBallCounter > 200:
                    self.isPlaying = False
            else: 
                self.ballPos = center
                self.noBallCounter = 0
                self.isPlaying = True

            if self.isPlaying: #everything else is contained in this if statement
                
                rodPoints = cvmethods.getRodPoints(frame)[0] #get rod data

                objects = self.ct.update(rodPoints) #and update

                self.rodPos = []
                for i in range(0, len(objects.items())): #each item is (objectId, centroid)
                    print(objects.items())
                    self.rodPos.append([list(objects.items())[i][0]/frame.shape[1]]) #0 for the x value, normalize it


                #essentially a heuristic
                onnxMatrix = [1, 1]
                if keyboard.read_key() == "q":
                    onnxMatrix[0] = 0
                elif keyboard.read_key() == "w":
                    onnxMatrix[0] = 2
                if keyboard.read_key() == "e":
                    onnxMatrix[1] = 0
                elif keyboard.read_key() == "r":
                    onnxMatrix[1] = 2

                linVel, rotVel = self.oh.rawOutputToVel(self.rodPos, self.rodRot, onnxMatrix) #run onnx on manufactured output
                linSteps, rotSteps = self.oh.velToSteps(linVel, rotVel)
                sendStr = str(linSteps) + "," + str(rotSteps) + ",0,0,0,0,\n" #format
                sendStr = bytes(sendStr, 'utf-8')
                self.ser.write(sendStr) #send to arduino

                if self.totalStepCounter % self.readRotCounterLim == 0: #check if we need to update rotation values
                    if self.ser.in_waiting: #see if serial has stuff in it
                        serLine = int(self.ser.readline().strip('\n')) #format the line
                        if serLine == self.specialNumber: #see if we have terminating number
                            rodMaskArray = [1, 3, 5] 
                            for i in range(0, 3):
                                serLine = int(self.ser.readline().strip('\n'))
                                self.rodRot[rodMaskArray[i]] = self.oh.stepsToRot(serLine) #update the changes

                cv2.imshow("frame", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

    def keyboardControlThrees(self):
        while True:
            self.totalStepCounter += 1 #update counters
            frame = self.newFrame() #make a new frame
            ball, center = cvmethods.getBallPos(frame) #get ball data
            if center == None:  #if it doesn't see the ball, power off
                self.noBallCounter += 1 #ball pos doesn't update if ball not found
                if self.noBallCounter > 200:
                    self.isPlaying = False
            else: 
                self.ballPos = center
                self.noBallCounter = 0
                self.isPlaying = True

            if self.isPlaying: #everything else is contained in this if statement
                
                rodPoints = cvmethods.getRodPoints(frame)[0] #get rod data

                objects = self.ct.update(rodPoints) #and update

                self.rodPos = []
                for i in range(0, len(objects.items())): #each item is (objectId, centroid)
                    print(objects.items())
                    self.rodPos.append([list(objects.items())[i][0]/frame.shape[1]]) #0 for the x value, normalize it


                #essentially a heuristic
                onnxMatrix = [1, 1, 1, 1, 1, 1]
                if keyboard.read_key() == "q":
                    onnxMatrix[0] = 0
                elif keyboard.read_key() == "w":
                    onnxMatrix[0] = 2
                if keyboard.read_key() == "e":
                    onnxMatrix[3] = 0
                elif keyboard.read_key() == "r":
                    onnxMatrix[3] = 2
                if keyboard.read_key() == "a":
                    onnxMatrix[1] = 0
                elif keyboard.read_key() == "s":
                    onnxMatrix[1] = 2
                if keyboard.read_key() == "d":
                    onnxMatrix[4] = 0
                elif keyboard.read_key() == "f":
                    onnxMatrix[4] = 2
                if keyboard.read_key() == "z":
                    onnxMatrix[2] = 0
                elif keyboard.read_key() == "x":
                    onnxMatrix[2] = 2
                if keyboard.read_key() == "c":
                    onnxMatrix[5] = 0
                elif keyboard.read_key() == "v":
                    onnxMatrix[5] = 2

                linoffSteps, linmidSteps, lindefSteps, rotoffSteps, rotmidSteps, rotdefSteps = self.oh.runOnnxThrees(self.ballPos, self.rodPos, self.rodRot) #run onnx

                sendStr = str(linoffSteps) + "," + str(rotoffSteps) + "," + str(linmidSteps) + "," + str(rotmidSteps) + "," + str(lindefSteps) + "," + str(rotdefSteps) + "," + "\n" #format
                sendStr = bytes(sendStr, 'utf-8')
                self.ser.write(sendStr) #send to arduino

                if self.totalStepCounter % self.readRotCounterLim == 0: #check if we need to update rotation values
                    if self.ser.in_waiting: #see if serial has stuff in it
                        serLine = int(self.ser.readline().strip('\n')) #format the line
                        if serLine == self.specialNumber: #see if we have terminating number
                            rodMaskArray = [1, 3, 5] 
                            for i in range(0, 3):
                                serLine = int(self.ser.readline().strip('\n'))
                                self.rodRot[rodMaskArray[i]] = self.oh.stepsToRot(serLine) #update the changes

                cv2.imshow("frame", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
        
    def newFrame(self):
        ret, frame = self.cap.read()
        frame = self.resize(frame, 50)
        return cvmethods.transformPerspective(frame, *self.transParams)

 
    def end(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def resize(self, frame, scale_percent):
        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        
        dim = (width, height)
        
        resized = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        return resized

if __name__ == "__main__":
    AFT = AutomatedFoosballTable()
    AFT.main()
    


