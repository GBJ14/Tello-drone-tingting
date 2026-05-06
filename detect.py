from djitellopy import Tello
from ultralytics import YOLO
import cv2

# load YOLOv8 nano model (downloads automatically first time, ~6MB)
model = YOLO('yolov8n.pt')

tello = Tello()
tello.connect()
print("Battery:", tello.get_battery())
tello.streamon()
frame_reader = tello.get_frame_read()

while True:
    frame = frame_reader.frame
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # run YOLO on the frame
    results = model(frame, conf=0.4, verbose=False)[0]

    # draw bounding boxes directly onto the frame
    annotated = results.plot()

    cv2.imshow("Tello Detection", annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

tello.streamoff()
tello.end()
cv2.destroyAllWindows()