import cv2
import numpy as np
import imutils

def findAruco(frame):
    this_aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
    params = cv2.aruco.DetectorParameters_create()
    corners, ids, rejected = cv2.aruco.detectMarkers(frame, this_aruco_dict, parameters=params)
    '''
            note: corners is a 4d tuple, like:
                (array([[[128, 319]
                  [211, 383]
                  [144, 473]
                  [590, 407]]], array(...))

            ids is a 2d array, like:
                [[1], [2], [3], [5]]
        '''
    if len(corners) > 0:
        ids.flatten()

        for (marker_corners, marker_id) in zip(corners, ids): #looping over the corners

            marker_corners = marker_corners.reshape((4, 2)) #make it into 4x2 array
            marker_corners = marker_corners.astype(int) #make the things all integers   
            top_left, top_right, bottom_right, bottom_left = marker_corners #name the corners
            
            #draw box around aruco
            cv2.line(frame, top_left, top_right, (0, 255, 0), 3) #image, first point, second point, color (BGR), thickness
            cv2.line(frame, top_right, bottom_right, (0, 255, 0), 3)
            cv2.line(frame, bottom_right, bottom_left, (0, 255, 0), 3)
            cv2.line(frame, bottom_left, top_left, (0, 255, 0), 3)
            
            #draw circle in center of aruco
            center_x = int((top_left[0] + bottom_right[0])/2)
            center_y = int((top_left[1] + bottom_right[1])/2)
            cv2.circle(frame, (center_x, center_y), 4, (0, 0, 255), -1) #image, center, radius, color, thick/fill

            #draw id text next to aruco
            cv2.putText(frame, str(marker_id), (top_left[0], top_left[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2) #img, text, org, font, fontscale, color, thickness
        
    if len(corners) == 4:
        fourArucos = True
    else:
        fourArucos = False
    
    return frame, corners, ids, fourArucos #fourArucos is the condition to move to the next part of init

def findPerspectiveTransform(frame, corners, ids):
    corners = np.array([corners[i].reshape((4, 2)).astype(int) for i in range (0, len(corners))]) #make it into 4x2 array

    framepoints = np.array([corners[np.where(ids == i)[0]][0][0] for i in range (0, 4)]).reshape(4, 2) #[0][0] because I want top left of every aruco

    heightA = np.sqrt((framepoints[0][0] - framepoints[3][0])**2 + (framepoints[0][1] - framepoints[3][1])**2)
    heightB = np.sqrt((framepoints[1][0] - framepoints[2][0])**2 + (framepoints[1][1] - framepoints[2][1])**2)
    maxHeight = max(int(heightA), int(heightB))
    
    widthA = np.sqrt((framepoints[0][0] - framepoints[1][0])**2 + (framepoints[0][1] - framepoints[1][1])**2)
    widthB = np.sqrt((framepoints[2][0] - framepoints[3][0])**2 + (framepoints[2][1] - framepoints[3][1])**2)
    maxWidth = max(int(widthA), int(widthB))
    
    input_points = np.array(framepoints, dtype = "float32")
    output_points = np.array([[0, 0], [maxWidth-1, 0], [maxWidth-1, maxHeight-1], [0, maxHeight-1]], dtype = "float32") #need to be float32s


    perspective = cv2.getPerspectiveTransform(input_points, output_points)
    return perspective, maxWidth, maxHeight 

def transformPerspective(frame, perspective, maxWidth, maxHeight):
    warped = cv2.warpPerspective(frame, perspective, (maxWidth, maxHeight))
    return warped
    
def getRodPoints(frame):
    pinkLower = (80, 10, 100)
    pinkUpper = (180, 120, 200)

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    cv2.imshow("blurred", blurred)

    mask = cv2.inRange(blurred, pinkLower, pinkUpper)
    mask = cv2.erode(mask, None, iterations=20)
    mask = cv2.dilate(mask, None, iterations=20)
    cv2.imshow("masked", mask)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    
    center = None
    pts = []
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    counter = 0
    if len(cnts) > 0:
        while counter < min(len(cnts), 4):
            c = cnts[counter]
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if radius > 10:
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                pts.append(center)
            
            counter = counter+1
    
    return pts