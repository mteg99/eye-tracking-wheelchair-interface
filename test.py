import cv2
import numpy as np
from GazeTracking.gaze_tracking import GazeTracking

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)

while True:
    _, input_frame = webcam.read()

    gaze.refresh(input_frame)   
    horizontal_ratio = gaze.horizontal_ratio()
    vertical_ratio = gaze.vertical_ratio()

    output_frame = np.zeros([1080,1920,3], dtype=np.uint8)
    output_frame.fill(255)

    if gaze.pupils_located:
        color = (255, 0, 0)
        horizontal_ratio = (horizontal_ratio - 0.5) / (0.75 - 0.5)
        vertical_ratio = (vertical_ratio - 0.5) / (0.75 - 0.5)
        x = int(1920 - horizontal_ratio * 1920)
        y = int(vertical_ratio * 1080)
        cv2.line(output_frame, (x - 10, y), (x + 10, y), color)
        cv2.line(output_frame, (x, y - 10), (x, y + 10), color)

    cv2.putText(output_frame, "Horizontal ratio:  " + str(horizontal_ratio), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    cv2.putText(output_frame, "Vertical ratio: " + str(vertical_ratio), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

    cv2.namedWindow("Test", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Test",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Test", output_frame)

    if cv2.waitKey(1) == 27:
        break
   
webcam.release()
cv2.destroyAllWindows()
