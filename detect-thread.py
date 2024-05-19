from collections import defaultdict
import threading
import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import datetime
import os
import telegram_utils as telegram

# Get path of current file
dir_path = os.path.dirname(os.path.realpath(__file__))
# telegram
annotator = None
sent_each = 15  # send each 15 seconds


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
    cv2.putText(frame, f"Canh bao!!!
                Co {total_person} nguoi trong vung cam", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 255), 1)
    return frame


def sent_alert(frame, total_person):
    # New thread to send telegram
    current_time = datetime.datetime.utcnow()
    cv2.imwrite(dir_path + f"/assets/alert.png",
                cv2.resize(frame, dsize=None, fx=0.4, fy=0.4))
    time = (current_time + datetime.timedelta(hours=7)
            ).strftime("%Y-%m-%d %H:%M:%S")
    telegram.send_message_with_photo(
        f"Phát hiện có {total_person} người xâm nhập\n {time} \n", dir_path + f"/assets/alert.png")


def run_tracker_in_thread(filename, model, file_index):
    # Store the box points
    box_points = []
    detected = False
    track_info = defaultdict(lambda: [])
    track_history = defaultdict(lambda: [])
    video = cv2.VideoCapture(filename, cv2.CAP_DSHOW)  # Read the video file

    while video.isOpened():
        ret, frame = video.read()  # Read the video frames
        total_person = 0

        # frame = cv2.flip(frame, 1)

        # Exit the loop if no more frames in either video
        if ret:
            # Draw box lines
            for point in box_points:
                cv2.circle(frame, (point[0], point[1]), 5, (0, 255, 0), -2)
            cv2.polylines(frame, [np.int32(box_points)], isClosed=False, color=(
                255, 255, 153), thickness=2)

            if detected:
                # Track objects in frames if available
                results = model.track(
                    frame, persist=True, classes=0, verbose=False)
                frame = plot_bboxes(results[0], frame)

            # Get the boxes and track IDs
                boxes = results[0].boxes.xywh.cpu()
                if results[0].boxes.id is not None:
                    track_ids = results[0].boxes.id.int().cpu().tolist()

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

                        # Check if the center point is inside the box
                        isInsided = isInside(box_points, points[-1][-1])
                        if isInsided:
                            total_person += 1
                            # add text alert to frame
                            frame = alert(frame, total_person)
                            # sent alert to telegram
                            current_time = datetime.datetime.utcnow()
                            if (track_id not in track_info):
                                track_info[track_id] = None
                            for tid, sent_time in list(track_info.items()):
                                if (sent_time is None) or tid == track_id and (current_time - sent_time).total_seconds() > sent_each:
                                    # sent tele
                                    alert_thread = threading.Thread(
                                        target=sent_alert, args=(frame, total_person))
                                    alert_thread.start()
                                    # update sent time
                                    track_info[track_id] = current_time
            # Get the points
            if cv2.getWindowProperty(f"Tracking_Stream_{file_index}", cv2.WND_PROP_VISIBLE) > 0:
                cv2.setMouseCallback(
                    f"IDS Tracking Stream {file_index}", handle_left_click, box_points)
            # else:
            #     print(
            #         f"Cửa sổ 'Tracking_Stream_{file_index}' không tồn tại hoặc đã bị đóng.")

            # Display the frames
            cv2.imshow(f"IDS Tracking Stream {file_index}", frame)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            elif key == 13:
                box_points.append(box_points[0])
                detected = True

    # Release video sources
    video.release()


# Load the models
model1 = YOLO('yolov8n.pt')
model2 = YOLO('yolov8n.pt')  # -seg

# Define the video files for the trackers
video_file1 = 0  # 0 for webcam
video_file2 = 1  # 1 for external camera

# Create the tracker threads
tracker_thread1 = threading.Thread(
    target=run_tracker_in_thread, args=(video_file1, model1, 1), daemon=True)
tracker_thread2 = threading.Thread(
    target=run_tracker_in_thread, args=(video_file2, model2, 2), daemon=True)

# Start the tracker threads
# tracker_thread1.start()
tracker_thread2.start()

# Wait for the tracker threads to finish
# tracker_thread1.join()
tracker_thread2.join()

# Clean up and close windows
cv2.destroyAllWindows()
