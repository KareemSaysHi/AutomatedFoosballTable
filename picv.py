import time
import cv2
#include <opencv2/aruco.hpp>
import numpy as np
import cv2
import imutils
from random import *
import time
import serial
import math



#CV stuff

def initPoints(cap, warped, pts):
    hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV).astype("float32")

    hsv[:,:,2] = hsv[:,:,2]*2
    hsv[:,:,2] = np.clip(hsv[:,:,2], 0, 255)
    
    frame = cv2.cvtColor(hsv.astype('uint8'), cv2.COLOR_HSV2BGR)

    cv2.imshow('frame', frame)
    
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY_INV)[1]
    cv2.imshow('thresh', thresh)
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    
    number = 0
    for c in cnts:
        M = cv2.moments(c)
        
        if M["m00"] > 10 and M["m00"] < 1000:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.drawContours(frame, [c], -1, (0, 255, 255), 2)
            cv2.circle(frame, (cx, cy), 7, (255, 255, 255), 2)
            cv2.putText(frame, str(number), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0),2)
            pts.append([cx, cy])
            number += 1
    print(pts)
    cv2.imshow('points', frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return frame, pts

def checkIfRed(points, image, pos1, pos2):
    #print (pos1)
    #print (pos2)
    
    imageCopy = image
    
    cv2.imshow('image', image)
    
    
    mask = np.zeros(image.shape[:2], dtype='uint8')
    
    if len(points) > 1:
        cv2.line(mask, (points[pos1][0], points[pos1][1]), (points[pos2][0], points[pos2][1]), (255, 255, 255), 15) 

    masked = cv2.bitwise_and(imageCopy, imageCopy, mask=mask)
    
    #cv2.imshow("masked", masked)

    lower_red = np.array([0, 50, 0])
    upper_red = np.array([100, 255, 100])
    
    redMask = cv2.inRange(masked, lower_red, upper_red)
    redMaskApplied = cv2.bitwise_and(masked, masked, mask=redMask)
    
    redMaskApplied = cv2.GaussianBlur(redMaskApplied, (5, 5), 0)
    
    #cv2.imshow("redMask", redMaskApplied)


    threshMask = cv2.cvtColor(redMaskApplied, cv2.COLOR_BGR2GRAY)
    final = cv2.threshold(threshMask, 1, 255, cv2.THRESH_BINARY)[1]

    #cv2.imshow("final", final)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows();

    
    cntsMask = cv2.findContours(final, cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)
    cntsMask = imutils.grab_contours(cntsMask)
    if len(cntsMask) != 0:
        areaSum = 0
        for c in cntsMask:
            MMask = cv2.moments(c)
            areaSum += MMask["m00"]
            cv2.drawContours(final, [c], -1, (0, 255, 255), 2)
        if areaSum > 700:
            return 1
        else:
            return 0
    else:
        return 0
    
def checkIfSame(old, new):
    diff = cv2.subtract(new, old)
    grayDiff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    grayDiffThresh = cv2.threshold(grayDiff, 30, 255, cv2.THRESH_BINARY)[1]

    if cv2.countNonZero(grayDiffThresh) == 0:
        print("nodiff")
        return True
    else:
        print("diff") 
        return False    
    
def checkPlayerMove(frame, points, boardRead):
        for i in range (0, 6):
            for j in range (0, 6):
                if i >= j:
                    boardRead.append(-1)
                else:
                    boardRead.append(checkIfRed(points, frame, i, j))
        return boardRead
    
#END OF CV STUFF FOR A BIT
    
#AI CV MIX FUNC
    
def cv2ai(aiList, cvList):
    for i in range (0, 6):
        for j in range (0,6):
            cvPos = 6*i + j
            if cvList[cvPos] == 1:
                aiList[i][j] = 1
    print (aiList)
    return aiList
                
                
def order_points(pts):
    
    rect = np.zeros((4, 2), dtype="float32")
    
    s = np.sum(pts, axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    d = np.diff(pts, axis=1)
    print(d)
    rect[1] = pts[np.argmin(d)]
    rect[3] = pts[np.argmax(d)]
    
    return rect
 
def four_point_transform(img, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    
    heightA = np.sqrt(((tr[0]-br[0]) ** 2) + ((tr[1]-br[1]) ** 2))
    heightB = np.sqrt(((tl[0]-bl[0]) ** 2) + ((tl[1]-bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    
    widthA = np.sqrt(((tr[0]-tl[0]) ** 2) + ((tr[1]-tl[1]) ** 2))
    widthB = np.sqrt(((br[0]-bl[0]) ** 2) + ((br[1]-bl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    
    dst = np.array([[0, 0], [maxWidth-1, 0], [maxWidth-1, maxHeight-1], [0, maxHeight-1]], dtype = "float32")
    
    M  = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))
    
    #print("width ", warped.shape[1])
    #print("height ", warped.shape[0])
    
    return warped

def findRedPoints(image):
    points = []
    imageCopy = image
    
    #print (image[:,:,2])
    for thing in image[:,:,2]:
        for otherThing in thing:
            if otherThing < 100:
                otherThing = 0
            else:
                otherThing = 255
        
    cv2.imshow("sss", image)
    
    hsv = cv2.cvtColor(imageCopy, cv2.COLOR_BGR2HSV).astype("float32")

    hsv[:,:,2] = hsv[:,:,2]*2
    hsv[:,:,2] = np.clip(hsv[:,:,2], 0, 255)
    
    imageCopy = cv2.cvtColor(hsv.astype('uint8'), cv2.COLOR_HSV2BGR)

    lower_red = np.array([0, 0, 50])
    upper_red = np.array([100,100,255])
    
    redMask = cv2.inRange(imageCopy, lower_red, upper_red)
    
    redMaskApplied = cv2.GaussianBlur(redMask, (5, 5), 0)
    
    cv2.imshow("redMask", redMaskApplied)

    final = cv2.threshold(redMaskApplied, 1, 255, cv2.THRESH_BINARY)[1]
    
    cv2.imshow("final", final)
    
    cntsMask = cv2.findContours(final, cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)
    cntsMask = imutils.grab_contours(cntsMask)
    
    if len(cntsMask) != 0:
        for c in cntsMask:
            M = cv2.moments(c)
            print (M["m00"])
            if M["m00"] > 500 and M["m00"] < 3000: 
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.drawContours(image, [c], -1, (0, 255, 255), 2)
                cv2.circle(image, (cx, cy), 7, (255, 255, 255), 2)
                points.append([cx, cy])
    else:
        pass
    cv2.circle(image, (410, 448), 7, (255, 255, 255), -1)

    cv2.imshow("image", image)

    return points
  
def cvToMove(tMatrix, x, y):
    xyMatrix = np.array([[x], [y], [1]])
    moveMatrix = tMatrix@xyMatrix
    print(moveMatrix)
    xMove = moveMatrix[0][0]
    yMove = moveMatrix[1][0]
    movePos = "X" + str(int(xMove)) + ",Y" + str(int(yMove)) + "\n"
    print(movePos)
    movePosb = bytes(movePos, 'utf-8')
    ser.write(movePosb)
    
def drawLine(tMatrix, x1, y1, x2, y2, ppl): #points per line
    cvToMove(tMatrix, x1, y1)
    time.sleep(2)
    ser.write(b'D\n')
    time.sleep(.2)
    
    xNew = float(x1)
    yNew = float(y1)
    
    for i in range(0, ppl):
        xNew = xNew + float(x2-x1)/ppl
        yNew = yNew + float(y2-y1)/ppl
        cvToMove(tMatrix, xNew, yNew)
        print([xNew, yNew, i])

        time.sleep(.05)
    time.sleep(1)
    ser.write(b'U\n')

    

cap = cv2.VideoCapture(0)
ret, frame = cap.read()

while cap.isOpened():
    for i in range(0, 6):
        ret, frame = cap.read()
    warped = four_point_transform(frame, warpPoints)
    
    hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV).astype("float32")

    hsv[:,:,2] = hsv[:,:,2]*2
    hsv[:,:,2] = np.clip(hsv[:,:,2], 0, 255)
    
    image = cv2.cvtColor(hsv.astype('uint8'), cv2.COLOR_HSV2BGR)
    
    # delete this after testing is done:
    '''while True:
        coordxtest = int(input("choose an x pixel"))
        coordytest = int(input("choose a y pixel"))
        cvToMove(transformationMatrix, coordxtest, coordytest)
        time.sleep(5)
        ser.write(b'X0,Y-179.65\n') #out of da wai
        time.sleep(3)'''





        
    
    playerMove(lines, player, warped, pts)
    
    
    #print(lines)
    aiMove(lines, ai)
    print(lines) 
    

cv2.destroyAllWindows()
cap.release()
