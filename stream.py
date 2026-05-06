from djitellopy import Tello
import cv2

tello = Tello()
tello.connect()
print("Battery:", tello.get_battery())

tello.streamon()
frame_reader = tello.get_frame_read()

while True:
    frame = frame_reader.frame
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # fix colors
    cv2.imshow("Tello Stream", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

tello.streamoff()
tello.end()
cv2.destroyAllWindows()