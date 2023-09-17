import cv2
import numpy as np
from imutils.video import VideoStream
from yolodetect import YoloDetect
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

model = YoloDetect()
# video = VideoStream(src=dir_path + "/video.mp4").start()
video = VideoStream(src=0).start()

points = []

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
    frame = video.read()
    frame = cv2.flip(frame, 1)

    # Ve ploygon
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
    cv2.imshow("IDS", frame)

    cv2.setMouseCallback('IDS', handle_left_click, points)

video.stop()
cv2.destroyAllWindows()
