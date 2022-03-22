import cvmethods
import cv2
import time
import sys
import imutils
import numpy as np
from centroidtracker import CentroidTracker
from onnxhelper import OnnxHelper

class AutomatedFoosballTable():
    
    def __init__(self):
        #define some standard values:
        self.isPlaying = False
        self.rodPos = [0, 0, 0, 0, 0, 0]
        self.rodRot = [None, 0, None, 0, None, 0]
        self.ballPos = 0
        self.noBallCounter = 0

        self.ct = CentroidTracker()
        self.oh = OnnxHelper()

        try:
            self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        except:
            self.cap = cv2.VideoCapture(0)
        #self.cap.set(3, 1920)
        #self.cap.set(4, 1080)

        #Look for four aruco tags

        while True: 
            ret, frame = self.cap.read()
            arucos = cvmethods.findAruco(frame)
            cv2.imshow("aruco", frame)
            if arucos[3] == True: #if four have been found
                break
            
            if cv2.waitKey(1) & 0xFF == ord('q'):  
                self.end()
                sys.exit("Manually exited the program")

            time.sleep(0.5)
        
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

        print("looking for rods")
        while True:
            frame = self.newFrame()
            frame = imutils.resize(frame, width=300)
            ball, center = cvmethods.getBallPos(frame)
            cv2.imshow("ball tracking", ball)
            if cv2.waitKey(1) & 0xFF == ord('q'):  
                self.end()
                sys.exit("Manually exited the program")
            elif cv2.waitKey(1) & 0xFF == ord('c'):  
                break
            time.sleep(0.02)

        cv2.destroyAllWindows()

        #Initialize rod positions

        #Find two rods

        counter = 0
        while True:
            frame = self.newFrame()
            frame = imutils.resize(frame, width=300)
            rodPoints = cvmethods.getRodPoints(frame)
            cv2.imshow("frame", frame)

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

            time.sleep(0.5)
        
        cv2.destroyAllWindows

        #get y coords of rods:
        yArray = ([rodPoints[i][1] for i in range (0, len(rodPoints))])
        ySortArray = np.argsort(yArray)
        sortedRodPoints = ([rodPoints[ySortArray[i]] for i in range (0, len(ySortArray))]) #sorted by y value

        for i in range (0, len(sortedRodPoints)):
            self.ct.register(sortedRodPoints[i], i) #register point with id i (increasing order in y)


    def main(self):
        while True:
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
                
                rodPoints = cvmethods.getRodPoints(frame) #get rod data
                objects = self.ct.update(rodPoints) #and update

                for i in range(0, len(objects.items())): #each item is (objectId, centroid)
                                self.rodPos.append[objects.items[i][0]/frame.shape[1]] #0 for the x value, normalize it

                for (objectId, centroid) in objects.items(): #just for visualization
                    text = "ID {}".format(objectId)
                    cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                ohParams = self.oh.setInputs(self.ballPos, self.rodPos, self.rodRot)
                ohResults = self.oh.runOnnx(ohParams)
                #oh to unity

                #UPDATE ROTATION HERE???
    

                

                cv2.imshow("frame", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

    def newFrame(self):
        ret, frame = self.cap.read()
        return cvmethods.transformPerspective(frame, *self.transParams)
 

    def end(self):
        self.cap.release()
        cv2.destroyAllWindows()
    

if __name__ == "__main__":
    AFT = AutomatedFoosballTable()
    AFT.main()
    