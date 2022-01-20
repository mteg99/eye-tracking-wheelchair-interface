import cv2
import pyglet
import numpy as np
from pykalman.pykalman import KalmanFilter

from GazeTracking.gaze_tracking import GazeTracking

from bufferless_video_capture import VideoCapture
from calibration_sequence import CalibrationSequence

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

WINDOW_NAME = "Kalman Test"

def initialize():
    camera = VideoCapture(1)
    cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(WINDOW_NAME,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    gaze_tracker = GazeTracking()
    return camera, gaze_tracker

def calibration_frame(dt, sequence, camera, gaze_tracker):
    x = sequence.get_x()
    y = sequence.get_y()
    display_dot((x, y), 1)
    frame = camera.read()
    gaze_tracker.refresh(frame)
    if not gaze_tracker.pupils_located:
        sequence.update((None, None))
    else:
        x = 1 - gaze_tracker.horizontal_ratio()
        y = gaze_tracker.vertical_ratio()
        sequence.update((x, y))

def display_dot(position, delay_ms):
    x = position[0]
    y = position[1]
    frame = blank_frame()
    cv2.circle(frame, (int(x), int(y)), 25, (255, 0, 0), -1)
    cv2.imshow(WINDOW_NAME, frame)
    wait(delay_ms)

def blank_frame():
    frame = np.zeros([SCREEN_HEIGHT,SCREEN_WIDTH, 3], dtype=np.uint8)
    frame.fill(255)
    return frame

def wait(delay_ms):
    key = cv2.waitKey(delay_ms)
    # exit on escape key
    if key == 27:
        exit(0)

clock = pyglet.clock.Clock()
camera, gaze_tracker = initialize()
display_dot((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), 1000)
calibration = CalibrationSequence(0.06, 8, 6, SCREEN_WIDTH, SCREEN_HEIGHT)
clock.schedule_interval(calibration_frame, calibration.dt, calibration, camera, gaze_tracker)
while not calibration.done:
    clock.tick()

measurements = calibration.get_measurements()

initial_state_mean = [
    SCREEN_WIDTH / 2,
    SCREEN_HEIGHT / 2,
    0,
    0,
    0,
    0
]

transition_matrix = [
    [1, 0, 1, 0, 0, 0],
    [0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 0],
    [0, 0, 0, 1, 0, 1],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1]
]

observation_matrix = [
    [1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0]
]

kf = KalmanFilter(
    transition_matrices = transition_matrix,
    observation_matrices = observation_matrix,
    initial_state_mean = initial_state_mean
)

kf = kf.em(measurements, n_iter=5)
means, covariances = kf.filter(measurements)
mean = means[-1]
covariance = covariances[-1]

while True:
    frame = camera.read()
    gaze_tracker.refresh(frame)
    if not gaze_tracker.pupils_located:
        continue
    x = 1 - gaze_tracker.horizontal_ratio()
    y = gaze_tracker.vertical_ratio()
    x, y = calibration.transform(x, y)

    mean, covariance = kf.filter_update(mean, covariance, (x, y))
    x = int(mean[0])
    y = int(mean[1])

    display_dot((x, y), 1)
