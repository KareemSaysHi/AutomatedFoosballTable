import cv2
import cvmethods
import imutils
import numpy as np

class TestClass():
    def __init__(self):
        cap = cv2.VideoCapture(-1)
        ret, frame = cap.read()
        cap.set(3, 960)
        cap.set(4, 540)
        while True: 
            ret, frame = cap.read()
            frame = self.resize(frame, 50)
            arucos = cvmethods.findAruco(frame)
            cv2.imshow("aruco", frame)
            if arucos[3] == True: #if four have been found
                break
            
            if cv2.waitKey(1) & 0xFF == ord('q'):  

                cv2.destroyAllWindows()
                cap.release()
                sys.exit("Manually exited the program")
        
        cv2.destroyAllWindows()
        cv2.imshow("og", frame)
        corners = arucos[1]
        ids = arucos[2]

        pTrans = cvmethods.findPerspectiveTransform(frame, corners, ids)
        pTrans = list(pTrans)
        print(pTrans[1])
        #for i in range (0, 3):
        #    pTrans[0][i] = np.divide(np.array(pTrans[0][i]), 2)
        #pTrans[1] = pTrans[1]//2
        #pTrans[2] = pTrans[2]//2
        
        #don't need this!
        
        self.transParams = list(pTrans)
        frame = cvmethods.transformPerspective(frame, *self.transParams)
        #frame = imutils.resize(frame, width=300)

        cv2.imshow("warped", frame)
        print("press c to continue, and q to quit")
        
        while True:      
            if cv2.waitKey(1) & 0xFF == ord('q'):  
                self.end()
            elif cv2.waitKey(1) & 0xFF == ord('c'):  
                break

        cv2.destroyAllWindows()
        
        while True: 
            frame = self.newFrame(cap)

            height, width = frame.shape[:2]
            print(height)
            print(width)

            ball, center = cvmethods.getBallPos(frame)
            cv2.imshow("ball tracking", ball)

            if cv2.waitKey(1) & 0xFF == ord('q'):  
 
                cv2.destroyAllWindows()
                cap.release()
                sys.exit("Manually exited the program")
        cv2.destroyAllWindows()
        cap.release()
    
    def resize(self, frame, scale_percent):
        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        
        dim = (width, height)
        
        resized = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        return resized
    
    def newFrame(self, cap):
        ret, frame = cap.read()
        #frame = self.resize(frame, 50)
        return cvmethods.transformPerspective(frame, *self.transParams)

tc = TestClass()

