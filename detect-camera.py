from collections import defaultdict
import cv2
import numpy as np
from ultralytics import YOLO
import os
from shapely.geometry import Point
from ultralytics.utils.plotting import Annotator, colors
from shapely.geometry.polygon import Polygon
import telegram_utils as telegram
import email_utils as email
import datetime
import threading

# Load the YOLOv8 model
model = YOLO('yolo11n.pt')


# Open webcam
# 0 for the default webcam, you can change it if you have multiple webcams
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Store the track history
track_history = defaultdict(lambda: [])
track_info = defaultdict(lambda: [])

# Store the box points
box_points = []
detected = False

# Get path of current file
dir_path = os.path.dirname(os.path.realpath(__file__))

# telegram
sent_each = 15  # send each 15 seconds

############### Function ##################
def handle_left_click(event, x, y, flags, points):  # Define the mouse callback function
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append([x, y])


def isInside(box_points, center_point):  # Check if the center point is inside the box
    polygon = Polygon(box_points)
    center_point = Point(center_point)
    result = polygon.contains(center_point)
    return result


def plot_bboxes(results, frame):
    annotator = Annotator(frame, 2)
    boxes = results.boxes.xyxy.cpu()
    clss = results.boxes.cls.cpu().tolist()
    for box, cls in zip(boxes, clss):
        annotator.box_label(
            box, color=colors(int(cls), True))
    return frame


def alert(frame, total_person):
    cv2.putText(frame, f"Co {total_person} nguoi trong vung cam!!!", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 255), 2)
    return frame


def sent_alert(frame, total_person, current_time):
    # New thread to send telegram
        cv2.imwrite(dir_path + f"/assets/alert.png",
                    cv2.resize(frame, dsize=None, fx=0.4, fy=0.4))
        time = (current_time + datetime.timedelta(hours=7)
                ).strftime("%Y-%m-%d %H:%M:%S")
        sent_with = os.environ.get("SENT_WITH")
        if(sent_with == "telegram"):
            telegram.send_message_with_photo(
                f"Phát hiện có {total_person} người xâm nhập\n {time} \n", os.path.join(dir_path, "assets", "alert.png"))
        elif(sent_with == "email"):
            email.send_email_with_image(os.environ.get("TO_EMAIL"), os.path.join(dir_path, "assets", "alert.png"),
            f"Phát hiện có {total_person} người xâm nhập\n {time} \n")
        else:
            print("Not sent alert\nCheck TO_EMAIL or CHAT_ID in .env")
############### End Function ##################


# Loop through the webcam frames
while cap.isOpened():
    total_person = 0
    # Read a frame from the webcam
    success, frame = cap.read()
    # Flip a frame camera
    # frame = cv2.flip(frame, 1)

    if success:
        # Draw box lines
        for point in box_points:
            cv2.circle(frame,
                       (point[0], point[1]), 4, (0, 0, 255), -2)
        cv2.polylines(frame, [np.int32(box_points)], isClosed=False, color=(
            230, 230, 230), thickness=2)

        # Detect objects in the frame if already detected
        if detected:
            # Run YOLOv11 tracking on the frame, persisting tracks between frames
            results = model.track(
                frame, persist=True, classes=0, verbose=False)
            frame = plot_bboxes(results[0], frame)

            # Get the boxes and track IDs
            boxes = results[0].boxes.xywh.cpu()
            if results[0].boxes.id is not None:
                track_ids = results[0].boxes.id.int().cpu().tolist()
                # Get center point of person
                for box, track_id in zip(boxes, track_ids):
                    x, y, w, h = box
                    track = track_history[track_id]
                    track.append((float(x), float(y)))  # x, y center point
                    if len(track) > 30:  # retain 90 tracks for 90 frames
                        track.pop(0)
                    points = np.hstack(track).astype(
                        np.int32).reshape((-1, 1, 2))
                    cv2.polylines(frame, [points], isClosed=False, color=(
                        0, 255, 0), thickness=2)  # show the track history

                    isInsided = isInside(box_points, points[-1][-1])
                    if isInsided:
                        total_person += 1
                        # add text alert to frame
                        frame = alert(frame, total_person)
                        # sent alert to telegram
                        current_time = datetime.datetime.now(datetime.UTC)
                        track_info.setdefault(track_id, None)
                        for tid, sent_time in list(track_info.items()):
                            if (sent_time is None) or tid == track_id and (current_time - sent_time).total_seconds() > sent_each:
                                # sent tele
                                alert_thread = threading.Thread(
                                    target=sent_alert, args=(frame, total_person, current_time))
                                alert_thread.start()
                                # update sent time
                                track_info[track_id] = current_time

        # Display the annotated frame
        cv2.imshow("IDS Streaming", frame)

        # Get the points
        if not detected:
            cv2.setMouseCallback(
                'IDS Streaming', handle_left_click, box_points)

        key = cv2.waitKey(1)
        if key == ord("q"):  # q key
            break
        elif key == 13:  # enter key
            box_points.append(box_points[0])
            detected = True
    else:
        # Break the loop if the webcam stream is interrupted
        break

# Release the webcam capture object and close the display window
cap.release()
cv2.destroyAllWindows()
