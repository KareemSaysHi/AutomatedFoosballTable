import cv2
import numpy as np

'''
add fiducials to detect what rod i'm looking at??

'''

desired_aruco_dictionary = "DICT_ARUCO_ORIGINAL"
aruco_marker_id = 1
output_filename = "DICT_ARUCO_ORIGINAL_id1.png"
 
# The different ArUco dictionaries built into the OpenCV library. 
ARUCO_DICT = {
  "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
  "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
  "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
  "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
  "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
  "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
  "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
  "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
  "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
  "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
  "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
  "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
  "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
  "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
  "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
  "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
  "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL
}

def main():

    this_aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)

    this_marker = np.zeros((300,300), dtype="uint8")
    cv2.aruco.drawMarker(this_aruco_dict, aruco_marker_id, 300, this_marker, 1)

    params = cv2.aruco.DetectorParameters_create()

    cap = cv2.VideoCapture(0)

    while True:

        ret, frame = cap.read()

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
            print('---------------------------new iteration---------------------------------')
            print('this is what corners look like')
            print(corners) 
            print('this is what ids look like')
            print(ids)
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

    
        cv2.imshow('frame',frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  
            break  

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print(__doc__)
    main()