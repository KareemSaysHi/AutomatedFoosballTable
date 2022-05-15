
import cvmethods
import cv2
import time
import sys
import imutils
import numpy as np
from centroidtracker import CentroidTracker
from helperonnx import OnnxHelper
import serial
import keyboard

class AutomatedFoosballTable():
    
    def __init__(self):
        
        self.deltaTime = 0.05
        try:
            self.ser = serial.Serial('/dev/ttyACM0', 250000, timeout=5)
            print("using ACM0")
        except:
            try:
                self.ser = serial.Serial('/dev/ttyACM1', 250000, timeout=5)
                print("using ACM1")
            except:
                print("going without serial comm")
        self.specialNumber = 123456789

        #define some standard values:
        self.isPlaying = False
        self.rodPos = [0, 0, 0, 0, 0, 0] #enemy, offense, enemy, mid, enemy, defense
        self.rodRot = [None, 0, None, 0, None, 0] #this is in terms of steps
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

            if len(rodPoints) == 6: #we found all rods
                counter = counter + 1
            else:
                counter = 0

            print(counter)

            if counter == 30: #for consistency
                break 
            
            if cv2.waitKey(1) & 0xFF == ord('q'):  
                self.end()
                sys.exit("Manually exited the program")

            time.sleep(0.02)
        
        cv2.destroyAllWindows()

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
        print("in keyboard")
        while True:
       	    print("TIME")
       	    print(time.time())
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
                    #print(objects.items())
                    self.rodPos.append(list(objects.items())[i][1][0]) #indices for the x value, normalize it
                    
                for (objectId, centroid) in objects.items(): #just for visualization
                    text = "ID {}".format(objectId)
                    cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                #print(self.rodPos)    
                
                self.correctRodPos(frame)
                
                #print("finished rod pos stuff")
                #print(self.rodPos) 
                
                #essentially a heuristic
                onnxMatrix = [1, 1]
                if keyboard.is_pressed("q"):
                    onnxMatrix[0] = 0
                elif keyboard.is_pressed("w"):
                    onnxMatrix[0] = 2
                if keyboard.is_pressed("e"):
                    onnxMatrix[1] = 0
                elif keyboard.is_pressed("r"):
                    onnxMatrix[1] = 2
		
                linVel, rotVel = self.oh.rawOutputToVel(self.rodPos, self.rodRot, onnxMatrix) #run onnx on manufactured output
                print("linvel")
                print(linVel)
                print("rotvel")
                print(rotVel)
                linSteps, rotSteps = self.oh.velToSteps(linVel, rotVel)
                sendStr = str(linSteps) + "," + str(rotSteps) + ",0,0,0,0,\n" #format
                print("sending this to arduino")
                print (sendStr)
                sendStr = bytes(sendStr, 'utf-8')
                
                #print("onnxmatrix")
                #print(onnxMatrix)
                
                #print("rotarray")
                #print(self.rodRot)
                
                self.ser.write(sendStr) #send to arduino
                
                print("lets see what homie arduino has to say")
                if self.ser.in_waiting:
                    serLine = str(self.ser.readline().decode("utf-8")) #format the line
                    print(serLine)

                if self.totalStepCounter % self.readRotCounterLim == 0: #check if we need to update rotation values
                    self.ser.flush() 
                    '''if self.ser.in_waiting: #see if serial has stuff in it
                        print(self.ser.in_waiting)
                        serLine = int(self.ser.readline().decode("utf-8")) #format the line
                        if serLine == self.specialNumber: #see if we have terminating number
                            rodMaskArray = [1, 3, 5] 
                            for i in range(0, 3):
                                serLine = int(self.ser.readline().strip('\n'))
                                self.rodRot[rodMaskArray[i]] = self.oh.stepsToRot(serLine) #update the changes
                    print("FIXED ROTATION LETS GO BABY")
                    print("FIXED ROTATION LETS GO BABY")
                    print("FIXED ROTATION LETS GO BABY")
                    print("FIXED ROTATION LETS GO BABY")
                    print("FIXED ROTATION LETS GO BABY")
                    print("FIXED ROTATION LETS GO BABY")
                    print("FIXED ROTATION LETS GO BABY")
                    print("FIXED ROTATION LETS GO BABY")
                    print("FIXED ROTATION LETS GO BABY")
                    print("FIXED ROTATION LETS GO BABY")'''

                cv2.imshow("frame", frame)
                
                print("a cycle has completed")
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord("m"):
                    break
        cv2.destroyAllWindows()
        cap.release()

    def keyboardControlThrees(self):
        print("in keyboard threes")
        while True:        
            startTime = time.time()
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
                    self.rodPos.append(list(objects.items())[i][1][0]) #0 for the x value
                print(self.rodPos)
                self.correctRodPos(frame)
                print(self.rodPos)
                
                print("collecting keyboard now")
                #essentially a heuristic
                onnxMatrix = [1, 1, 1, 1, 1, 1]
                if keyboard.is_pressed("q"):
                    onnxMatrix[0] = 0
                elif keyboard.is_pressed("w"):
                    onnxMatrix[0] = 2
                if keyboard.is_pressed("e"):
                    onnxMatrix[3] = 0
                elif keyboard.is_pressed("r"):
                    onnxMatrix[3] = 2
                if keyboard.is_pressed("a"):
                    onnxMatrix[1] = 0
                elif keyboard.is_pressed("s"):
                    onnxMatrix[1] = 2
                if keyboard.is_pressed("d"):
                    onnxMatrix[4] = 0
                elif keyboard.is_pressed("f"):
                    onnxMatrix[4] = 2
                if keyboard.is_pressed("z"):
                    onnxMatrix[2] = 0
                elif keyboard.is_pressed("x"):
                    onnxMatrix[2] = 2
                if keyboard.is_pressed("c"):
                    onnxMatrix[5] = 0
                elif keyboard.is_pressed("v"):
                    onnxMatrix[5] = 2
                    
                print(onnxMatrix)
                
                linoffSteps, linmidSteps, lindefSteps, rotoffSteps, rotmidSteps, rotdefSteps = self.oh.runOnnxThrees(self.ballPos, self.rodPos, self.rodRot, heuristic = True, manufacturedOutput = onnxMatrix) #run onnx

                sendStr = str(linoffSteps) + "," + str(rotoffSteps) + "," + str(linmidSteps) + "," + str(rotmidSteps) + "," + str(lindefSteps) + "," + str(rotdefSteps) + "," + "\n" #format
                print(sendStr);
                sendStr = bytes(sendStr, 'utf-8')
                self.ser.write(sendStr) #send to arduino
                '''
                if self.totalStepCounter % self.readRotCounterLim == 0: #check if we need to update rotation values
                    if self.ser.in_waiting: #see if serial has stuff in it
                        serLine = int(self.ser.readline().strip('\n')) #format the line
                        if serLine == self.specialNumber: #see if we have terminating number
                            rodMaskArray = [1, 3, 5] 
                            for i in range(0, 3):
                                serLine = int(self.ser.readline().strip('\n'))
                                self.rodRot[rodMaskArray[i]] = self.oh.stepsToRot(serLine) #update the changes
                '''

                cv2.imshow("frame", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("p"):
                    break
                    
                while(time.time() - startTime) < 0.1:
                    pass
                print(time.time() - startTime)
        
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
        
    def correctRodPos(self, frame):
    	for i in range (0, 6):
    	    self.rodPos[i] += int(2 / 23 * frame.shape[1]) #inches * pixels / inches
    	    self.rodPos[i] -= frame.shape[1]/2 #center it around 0
    	    self.rodPos[i] = self.rodPos[i] * 23 / frame.shape[1]
    	    
    	    
    	
        


if __name__ == "__main__":
    AFT = AutomatedFoosballTable()
    AFT.keyboardControlThrees()
    


