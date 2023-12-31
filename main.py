import cv2
import numpy as np
from yolodetect import YoloDetect
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dir_path = os.path.dirname(os.path.realpath(__file__))
load_dotenv(dotenv_path=dotenv_path)

model = YoloDetect()
video = cv2.VideoCapture(0)
points = []
if(os.getenv("enable_send_telegram") == "0"):
    print("Gửi tin nhắn tới telegram đang bị vô hiệu hóa")

def handle_left_click(event, x, y, flags, points):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append([x, y])


def draw_polygon (frame, points):
    for point in points:
        frame = cv2.circle( frame, (point[0], point[1]), 5, (0,0,255), -1)

    frame = cv2.polylines(frame, [np.int32(points)], False, (255,0, 0), thickness=1)
    return frame


detect = False
while True:
    ret, frame = video.read()
    frame = cv2.flip(frame, 1)
    
    if not ret:
        print("Không thể đọc khung hình từ camera.")
        break

    frame = draw_polygon(frame, points)

    if detect:
        frame = model.detect(frame= frame, points= points)

    key = cv2.waitKey(1)
    if key == 27: # esc key
        break
    elif key == 13: # enter key
        points.append(points[0])
        detect = True

    # show
    cv2.imshow("IDS video", frame)

    cv2.setMouseCallback('IDS video', handle_left_click, points)

video.release()
cv2.destroyAllWindows()
