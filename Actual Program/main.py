import cvmethods
import cv2
import time
import sys
import imutils
import numpy as np
from centroidtracker import CentroidTracker

class AutomatedFoosballTable():
    
    def __init__(self):
        try:
            self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        except:
            self.cap = cv2.VideoCapture(0)
            
        #Look for four aruco tags

        while True: 
            ret, frame = self.cap.read()
            frame = imutils.resize(frame, width=600)
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

        #Initialize rod positions

        #Find two rods

        counter = 0
        while True:
            frame = self.newFrame()
            rodPoints = cvmethods.getRodPoints(frame)
            cv2.imshow("frame", frame)

            print(len(rodPoints))
            print(counter)

            if len(rodPoints) == 2: #we found both rods
                print("we in here")
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

        self.ct = CentroidTracker()
        for i in range (0, len(sortedRodPoints)):
            self.ct.register(sortedRodPoints[i], i) #register point with id i (increasing order in y)

        #TESTING LOOP:

        while True:
            frame = self.newFrame()
            rodPoints = cvmethods.getRodPoints(frame)
            objects = self.ct.update(rodPoints)

            for (objectId, centroid) in objects.items():
                text = "ID {}".format(objectId)
                cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

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
    