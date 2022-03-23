import cv2
import pyglet
import numpy as np
from datetime import datetime
from eye_tracking.pykalman.pykalman import KalmanFilter
import socket
import sys
import pickle
import struct
import pyautogui

from eye_tracking.GazeTracking.gaze_tracking import GazeTracking

from eye_tracking.bufferless_video_capture import VideoCapture
from eye_tracking.calibration_sequence import CalibrationSequence

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
BUTTON_RADIUS = 200
TURN_COLOR = (0, 0, 255)
FORWARD_COLOR = (0, 255, 0)
LEFT_BUTTON_X = 335
GO_BUTTON_X = 960
RIGHT_BUTTON_X = 1585
LEFT_BUTTON_Y = 540
GO_BUTTON_Y = 260
RIGHT_BUTTON_Y = 540
BUTTONS = ["left", "go", "right"]

WINDOW_NAME = "Wheelchair Interface"

last_button = None

def initialize():
    camera = VideoCapture(0)
    cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    gaze_tracker = GazeTracking()
    return camera, gaze_tracker

def calibration_frame(dt, sequence, camera):
    x, y = sequence.get_position()
    display_dot((x, y), 1)
    frame = camera.read()
    sequence.push_frame(frame)

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
        calibration.__del__()
        exit(0)

def check_cursor(currentX, currentY):
    if (currentX >= (LEFT_BUTTON_X - BUTTON_RADIUS) and currentX <= (LEFT_BUTTON_X + BUTTON_RADIUS) 
    and currentY >= (LEFT_BUTTON_Y - BUTTON_RADIUS) and currentY <= (LEFT_BUTTON_Y + BUTTON_RADIUS)):
            return 'l'
    elif (currentX >= (GO_BUTTON_X - BUTTON_RADIUS) and currentX <= (GO_BUTTON_X + BUTTON_RADIUS) 
    and currentY >= (GO_BUTTON_Y - BUTTON_RADIUS) and currentY <= (GO_BUTTON_Y + BUTTON_RADIUS)):
            return 'f'
    elif (currentX >= (RIGHT_BUTTON_X - BUTTON_RADIUS) and currentX <= (RIGHT_BUTTON_X + BUTTON_RADIUS) 
    and currentY >= (RIGHT_BUTTON_Y - BUTTON_RADIUS) and currentY <= (RIGHT_BUTTON_Y + BUTTON_RADIUS)):
            return 'r'
    else:
        return 'h'

clock = pyglet.clock.Clock()
camera, gaze_tracker = initialize()
display_dot((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), 1000)
calibration = CalibrationSequence(0.04, 8, 6, SCREEN_WIDTH, SCREEN_HEIGHT, gaze_tracker)
# calibration = CalibrationSequence(0.04, 1, 1, SCREEN_WIDTH, SCREEN_HEIGHT, gaze_tracker)
clock.schedule_interval(calibration_frame, calibration.dt, calibration, camera)
while not calibration.done:
    clock.tick()

initial_state_mean = [
    SCREEN_WIDTH / 2,
    SCREEN_HEIGHT / 2,
    0,
    0,
    0,
    0
]

A, H, W, Q = calibration.get_kalman_parameters()

kf = KalmanFilter(
    transition_matrices = A,
    observation_matrices = H,
    transition_covariance = W,
    observation_covariance= Q,
    initial_state_mean = initial_state_mean
)

measurements = calibration.get_measurements()

means, covariances = kf.filter(measurements)
mean = means[-1]
covariance = covariances[-1]

initialize()
HOST, PORT = "0.0.0.0", 8089
    
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    print('Socket created')

    sock.bind((HOST, PORT))
    print('Socket bind complete')
    sock.listen(10)
    print('Socket now listening')

    conn, addr = sock.accept()
    print(f'{addr} connected')
    data = b'' ### CHANGED
    payload_size = struct.calcsize("Q") ### CHANGED

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

        # x, y = pyautogui.position()

        # Retrieve message size
        while len(data) < payload_size:
            data += conn.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0] ### CHANGED

        # Retrieve all data based on message size
        while len(data) < msg_size:
            data += conn.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        # Extract frame
        output_frame = pickle.loads(frame_data)
        output_frame = cv2.resize(output_frame, (SCREEN_WIDTH, SCREEN_HEIGHT), interpolation=cv2.INTER_AREA)


        # output_frame = blank_frame()
        output_frame = cv2.circle(output_frame, (LEFT_BUTTON_X, LEFT_BUTTON_Y), BUTTON_RADIUS, TURN_COLOR, 5)
        output_frame = cv2.circle(output_frame, (GO_BUTTON_X, GO_BUTTON_Y), BUTTON_RADIUS, FORWARD_COLOR, 5)
        output_frame = cv2.circle(output_frame, (RIGHT_BUTTON_X, RIGHT_BUTTON_Y), BUTTON_RADIUS, TURN_COLOR, 5)
        output_frame = cv2.circle(output_frame, (int(x), int(y)), 25, (255, 0, 0), -1)
        
        cv2.imshow(WINDOW_NAME, output_frame)
        wait(1)

        button = check_cursor(x, y)
        print(button)
        if (last_button != button):
            conn.sendall(bytes(button, "utf-8"))
            last_button = button
        else:
            conn.sendall(bytes('p', "utf-8"))