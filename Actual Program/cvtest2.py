import cvmethods
import cv2
import time
import sys
import imutils
import numpy as np
from centroidtracker import CentroidTracker
from onnxhelper import OnnxHelper
import serial

class AutomatedFoosballTable():
    
    def __init__(self):

        self.cap = cv2.VideoCapture(-1)
            
        self.cap.set(3, 960)
        self.cap.set(4, 540)
      
        #Look for four aruco tags

        while True: 
            ret, frame = self.cap.read()
            cv2.imshow("frame", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):  
                self.end()
                
                sys.exit("Manually exited the program")
        
        cv2.destroyAllWindows()
        
    def end(self):
        self.cap.release()
        cv2.destroyAllWindows()
    

if __name__ == "__main__":
    AFT = AutomatedFoosballTable()
    AFT.main()

