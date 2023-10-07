import cv2
from yolodetect import YoloDetect
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
model = YoloDetect()
image_path = dir_path + '/' + 'test.jpg'  # Đường dẫn đến ảnh

frame = cv2.imread(image_path)
frame = model.detect(frame= frame, points = [])
cv2.imshow("IDS photo", frame)

cv2.waitKey(0) # Chờ nhấn phím bất kì để thoát
cv2.destroyAllWindows()