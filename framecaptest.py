import cv2

vidcap = cv2.VideoCapture(0)
success,image = vidcap.read()
count = 0
while count < 32:
  cv2.imshow("frame%d.jpg" % count, image)     # save frame as JPEG file      
  success,image = vidcap.read()
  print('Read a new frame: ', success)
  count += 1
cv2.waitKey(0)
cv2.destroyAllWindows()