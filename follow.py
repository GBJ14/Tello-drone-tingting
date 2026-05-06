from djitellopy import Tello
from ultralytics import YOLO
import cv2

# --- CALIBRATION ---
# Stand exactly 150cm from the drone, note the pixel width of your bounding box
# then set KNOWN_DISTANCE and REFERENCE_PIXEL_WIDTH accordingly
KNOWN_DISTANCE = 150       # cm — how far you stood during calibration
KNOWN_PERSON_WIDTH = 50    # cm — average shoulder width
REFERENCE_PIXEL_WIDTH = 200  # pixels — bounding box width at calibration distance
                              # YOU NEED TO TUNE THIS

# focal length derived from calibration (pinhole camera model)
FOCAL_LENGTH = (REFERENCE_PIXEL_WIDTH * KNOWN_DISTANCE) / KNOWN_PERSON_WIDTH

MIN_DISTANCE = 20   # cm — won't fly closer than this
SPEED = 20
DEADZONE = 60

model = YOLO(r'C:\Users\elias\Desktop\yolov8n.pt')

tello = Tello()
tello.connect()
print("Battery:", tello.get_battery())
tello.streamon()
tello.takeoff()

frame_reader = tello.get_frame_read()

while True:
    frame = frame_reader.frame
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    frame_h, frame_w = frame.shape[:2]
    frame_cx = frame_w // 2
    frame_cy = frame_h // 2

    results = model(frame, conf=0.5, classes=[0], verbose=False)[0]

    lr, fb, ud, yaw = 0, 0, 0, 0

    if len(results.boxes) > 0:
        # pick most confident detection
        best = max(results.boxes, key=lambda b: float(b.conf[0]))
        x1, y1, x2, y2 = map(int, best.xyxy[0])

        obj_cx = (x1 + x2) // 2
        obj_cy = (y1 + y2) // 2
        box_w = x2 - x1  # use width for distance (more stable than height)

        # estimate real distance using pinhole model
        if box_w > 0:
            distance_cm = (KNOWN_PERSON_WIDTH * FOCAL_LENGTH) / box_w
        else:
            distance_cm = 999

        x_err = obj_cx - frame_cx
        y_err = frame_cy - obj_cy

        # yaw to center horizontally
        if abs(x_err) > DEADZONE:
            yaw = SPEED if x_err > 0 else -SPEED

        # up/down to center vertically
        if abs(y_err) > DEADZONE:
            ud = SPEED if y_err > 0 else -SPEED

        # forward/back based on real distance — STOP if too close
        if distance_cm > MIN_DISTANCE + 20:
            fb = SPEED      # too far, move closer
        elif distance_cm < MIN_DISTANCE:
            fb = -SPEED     # too close, back off
        # else within safe zone, don't move forward/back

        # draw info
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.circle(frame, (obj_cx, obj_cy), 5, (0, 255, 0), -1)
        cv2.putText(frame, f"Dist: {round(distance_cm)}cm", (x1, y1 - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, "TRACKING", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # safety warning on screen
        if distance_cm < MIN_DISTANCE:
            cv2.putText(frame, "TOO CLOSE", (frame_cx - 60, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

    else:
        # no target — rotate slowly to search
        yaw = SPEED
        cv2.putText(frame, "SEARCHING...", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)

    tello.send_rc_control(lr, fb, ud, yaw)

    cv2.circle(frame, (frame_cx, frame_cy), 5, (255, 0, 0), -1)
    cv2.imshow("Tello Follow", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

tello.land()
tello.streamoff()
tello.end()
cv2.destroyAllWindows()