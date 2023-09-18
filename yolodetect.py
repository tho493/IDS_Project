from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import cv2
import numpy as np
import os
import datetime
import threading
import telegram_utils as telegram
from dotenv import load_dotenv

dir_path = os.path.dirname(os.path.realpath(__file__))
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)


def isInside(points, centroid):
    polygon = Polygon(points)
    centroid = Point(centroid)
    if(os.getenv("debug") =="1"): print(polygon.contains(centroid))
    return polygon.contains(centroid)


class YoloDetect():
    def __init__(self, detect_class="person"):
        # Parameters
        self.classnames_file = dir_path + "\model\coco.names"
        self.weights_file = dir_path + "\model\yolov4-tiny.weights"
        self.config_file = dir_path + "\model\yolov4-tiny.cfg"
        self.conf_threshold = 0.5
        self.nms_threshold = 0.4
        self.detect_class = detect_class
        self.scale = 1 / 255
        self.model = cv2.dnn.readNet(self.weights_file, self.config_file)
        self.classes = None
        self.output_layers = None
        self.read_class_file()
        self.get_output_layers()
        self.last_alert = None
        self.alert_telegram_each = 15 #seconds

    def read_class_file(self):
        with open(self.classnames_file, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]

    def get_output_layers(self):
        layer_names = self.model.getLayerNames()
        self.output_layers = [layer_names[i - 1] for i in self.model.getUnconnectedOutLayers()]

    def draw_prediction(self, img, class_id, left, top, x_plus_w, y_plus_h, points):
        label = self.classes[class_id]
        color = (0, 255, 0)
        cv2.rectangle(img, (left, top), (x_plus_w, y_plus_h), color, 2)
        cv2.putText(img, label, (left - 10, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Tinh toan centroid
        centroid = ((left + x_plus_w) // 2, (top + y_plus_h) // 2)
        cv2.circle(img, centroid, 5, (color), -1)

        if isInside(points, centroid):
            img = self.alert(img)

        return isInside(points, centroid)

    def alert(self, img):
        cv2.putText(img, "ALARM!!!!", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        # New thread to send telegram after 15 seconds
        timenow = datetime.datetime.utcnow()
        if (self.last_alert is None) or (
                (timenow - self.last_alert).total_seconds() > self.alert_telegram_each):
            self.last_alert = timenow
            cv2.imwrite(dir_path + "/alert.png", cv2.resize(img, dsize=None, fx=0.2, fy=0.2))
            time = (timenow + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
            thread = threading.Thread(target=telegram.send_message_with_photo("ALARM!!!!" + "\n" + time + "\n", dir_path + "/alert.png"))
            thread.start()
        return img

    def detect(self, frame, points):
        blob = cv2.dnn.blobFromImage(frame, self.scale, (416, 416), (0, 0, 0), True, crop=False)
        self.model.setInput(blob)
        outs = self.model.forward(self.output_layers)

        # Loc cac object trong khung hinh
        class_ids = []
        confidences = []
        boxes = []

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if (confidence >= self.conf_threshold) and (self.classes[class_id] == self.detect_class):
                    center_x = int(detection[0] * frame.shape[1])
                    center_y = int(detection[1] * frame.shape[0])
                    w = int(detection[2] * frame.shape[1])
                    h = int(detection[3] * frame.shape[0])
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])

        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, self.nms_threshold)

        for i in indices:
            box = boxes[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]
            self.draw_prediction(frame, class_ids[i], round(left), round(top), round(left + width), round(top + height), points)

        return frame
