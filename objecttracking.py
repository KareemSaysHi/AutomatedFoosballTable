from scipy.spatial import distance as dist
import numpy as np
import cv2
import imutils

class CentroidTracker():
    def __init__(self):
        self.nextObjectId = 0
        self.objects = dict()
        #self.objects looks like:
        #{
        # objectId: centroid
        # 1: (11, 12)
        # 2: (21, 22)
        # 3: (31, 32)
        # }

    def register(self, centroid):
        self.objects[self.nextObjectId] = centroid
        self.nextObjectId += 1

    def update(self, centroids):
        inputCentroids = centroids
        #[
        # [12, 13],
        # [22, 23],
        # [32, 33]
        # ]

        #if we aren't tracking any objects yet
        #register them
        if len(self.objects) < len(inputCentroids):
            for i in range(0, len(inputCentroids)):
                self.register(inputCentroids[i])

        elif len(inputCentroids) == 0:
            return self.objects

        else:
            objectIds = list(self.objects.keys()) #[1, 2, 3]
            objectCentroids = list(self.objects.values()) #[(11, 12), (21, 22), (31, 32)]
            print("object centroids:")
            print(objectCentroids)

            print("input centroids:")
            print(inputCentroids)

            D = dist.cdist(np.array(objectCentroids), inputCentroids, 'euclidean')
            #D = [
            # [d_i1j1, d_i1j2, d_i1j3, ...]
            # [d_i2j1, d_i2j2, d_i2j3, ...]
            # ...
            # ]

            rows = D.min(axis=1).argsort() #minimim j for each i, then argsort

            #[1 0 2] smallest in row 1 (object id 1), second smallest in row 2, ...

            #D.min = [d_i1ja, d_i2jb, d_i1jc, d_i1jd, ...]
    
            #rows = [index of smallest d_ixjy, index of second smallest d_ixjy, ...]

            cols = D.argmin(axis=1)[rows] #minimumj for each i, actually sorted

            #rows = [smallest d_ixjy, second smallest d_ixjy, ...]

            #row, col equal to (this is the id with the smallest distance from the thing, this is the column that matches up with this distance)
            usedRows = set()
            usedCols = set()

            for (row, col) in zip(rows, cols):
                #(row, col) = (
                # index of kth smallest d_ixjy
                # kth smallest d_ixjy
                # )
                if row in usedRows or col in usedCols:
                    continue

                objectId = objectIds[row]
                self.objects[objectId] = inputCentroids[col]

                usedRows.add(row)
                usedCols.add(col)
        
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)

            if D.shape[0] >= D.shape[1]:
                for col in unusedCols:
                    self.register(inputCentroids[col])

        return self.objects

            #code should automatically use old pos if the other one not found


ct = CentroidTracker()

pinkLower = (80, 50, 150)
pinkUpper = (180, 120, 200)

cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=600)
    #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    cv2.imshow("blurred", blurred)

    mask = cv2.inRange(blurred, pinkLower, pinkUpper)
    mask = cv2.erode(mask, None, iterations=20)
    mask = cv2.dilate(mask, None, iterations=20)
    cv2.imshow("masked", mask)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    if len(cnts) > 1:
        print(len(cnts))
    
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
                pts.append([int(x), int(y)])
            
            counter = counter+1
    
    objects = ct.update(pts)

    for (objectId, centroid) in objects.items():
        text = "ID {}".format(objectId)
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    #print(pts)

    cv2.imshow("frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
