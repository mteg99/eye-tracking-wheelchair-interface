import cv2
import numpy as np

from GazeTracking.gaze_tracking import GazeTracking

from bufferless_video_capture import VideoCapture

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

WINDOW_NAME = "Wheelchair Interface"

def initialize():
    camera = VideoCapture(0)
    cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(WINDOW_NAME,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    gaze_tracker = GazeTracking()
    return camera, gaze_tracker

def calibrate(camera, gaze_tracker):
    display_instructions()
    display_countdown()

    margin = 50
    top_left = margin, margin
    top_right = SCREEN_WIDTH - margin, margin
    bottom_left = margin, SCREEN_HEIGHT - margin
    bottom_right = SCREEN_WIDTH - margin, SCREEN_HEIGHT - margin

    n_samples = 5
    initial_delay_sec = 1

    x_min_samples = []
    x_max_samples = []
    y_min_samples = []
    y_max_samples = []
    for position in [top_left, top_right, bottom_left, bottom_right]:
        display_dot(position, initial_delay_sec)
        x, y = capture_ratio_samples(camera, gaze_tracker, n_samples)

        if position == top_left or position == bottom_left:
            x_min_samples += x
        else:
            x_max_samples += x

        if position == top_left or position == top_right:
            y_min_samples += y
        else:
            y_max_samples += y

    print(x_min_samples)
    print(x_max_samples)
    print(y_min_samples)
    print(y_max_samples)

def display_instructions():
    display_text(
        [
            "To calibrate, focus on the dots as they appear in the corners.",
            "They will appear in this order: top left, top right, bottom left, bottom right."
        ],
        10
    )

def display_countdown():
    for i in ['3', '2', '1']:
        display_text([i], 1)

def display_text(lines, delay_sec):
    frame = blank_frame()
    for l in range(len(lines)):
        cv2.putText(
            frame,
            lines[l],
            (int(SCREEN_WIDTH / 8), int(SCREEN_HEIGHT / 4) + 100 * l),
            cv2.FONT_HERSHEY_DUPLEX,
            1,
            (255, 0, 0)
        )
    cv2.imshow(WINDOW_NAME, frame)
    wait(delay_sec * 1000)

def display_dot(position, delay_sec):
    x = position[0]
    y = position[1]
    frame = blank_frame()
    cv2.circle(frame, (int(x), int(y)), 25, (255, 0, 0), -1)
    cv2.imshow(WINDOW_NAME, frame)
    wait(delay_sec * 1000)

def capture_ratio_samples(camera, gaze_tracker, n):
    x_samples = []
    y_samples = []
    for s in range(n):
        frame = camera.read()
        gaze_tracker.refresh(frame)
        x_samples.append(1 - gaze_tracker.horizontal_ratio())
        y_samples.append(gaze_tracker.vertical_ratio())
    return x_samples, y_samples

def wait(delay_ms):
    key = cv2.waitKey(delay_ms)
    # exit on escape key
    if key == 27:
        exit(0)

def blank_frame():
    frame = np.zeros([SCREEN_HEIGHT,SCREEN_WIDTH, 3], dtype=np.uint8)
    frame.fill(255)
    return frame

def main():
    camera, gaze_tracker = initialize()

    calibrate(camera, gaze_tracker)

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

# while True:
#     _, input_frame = webcam.read()

#     gaze.refresh(input_frame)
#     horizontal_ratio = gaze.horizontal_ratio()
#     vertical_ratio = gaze.vertical_ratio()

#     output_frame = np.zeros([1080,1920,3], dtype=np.uint8)
#     output_frame.fill(255)

#     if gaze.pupils_located:
#         color = (255, 0, 0)
#         horizontal_ratio = (horizontal_ratio - 0.5) / (0.75 - 0.5)
#         vertical_ratio = (vertical_ratio - 0.5) / (0.75 - 0.5)
#         x = int(1920 - horizontal_ratio * 1920)
#         y = int(vertical_ratio * 1080)
#         cv2.line(output_frame, (x - 10, y), (x + 10, y), color)
#         cv2.line(output_frame, (x, y - 10), (x, y + 10), color)

#     cv2.putText(output_frame, "Horizontal ratio:  " + str(horizontal_ratio), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
#     cv2.putText(output_frame, "Vertical ratio: " + str(vertical_ratio), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

#     cv2.namedWindow("Test", cv2.WND_PROP_FULLSCREEN)
#     cv2.setWindowProperty("Test",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
#     cv2.imshow("Test", output_frame)

#     if cv2.waitKey(1) == 27:
#         break
   
# webcam.release()
# cv2.destroyAllWindows()
