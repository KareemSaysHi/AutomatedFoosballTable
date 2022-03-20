import cv2

pic = cv2.imread('cubesat.png')
pic = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)

for i in range (0, len(pic)):
    for j in range(0, len(pic[i])):
        if pic[i][j] < 150:
            pic[i][j] = 0
        if pic[i][j] < 200:
            pic[i][j] = 150
        else:
            pic[i][j] = 255

cv2.imshow("pic", pic)
cv2.waitKey(0) 
cv2.destroyAllWindows()
