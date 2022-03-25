import cv2
import pyglet
import numpy as np
from datetime import datetime
import socket
import sys
import pickle
import struct
import pyautogui

# sys.path.append('eye_tracker')
from eye_tracker.eye_tracker import EyeTracker
from frontend.window import Window
from frontend.user_interface import UserInterface
from frontend.button import Button
from eye_tracker.GazeTracking.gaze_tracking import GazeTracking

from utils.bufferless_video_capture import BufferlessVideoCapture
from eye_tracker.calibration_sequence import CalibrationSequence

screen_width, screen_height = pyautogui.size()

window = Window('Wheelchair Interface')
eye_tracker = EyeTracker(window)
eye_tracker.calibrate()

forward = Button(x=screen_width/2, y=screen_height/5, radius=screen_width/10, color=(0, 255, 0), command='f')
left = Button(x=screen_width/8, y=screen_height*(2/3), radius=screen_width/10, color=(0, 0, 255), command='l')
right = Button(x=screen_width*(7/8), y=screen_height*(2/3), radius=screen_width/10, color=(0, 0, 255), command='r')
ui = UserInterface([forward, left, right], debug_mode=True)

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
        x, y = eye_tracker.get_cursor()
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
        output_frame = cv2.resize(output_frame, (screen_width, screen_height), interpolation=cv2.INTER_AREA)
        
        if not x or not y:
            continue
        command = ui.update_cursor(x, y)
        output_frame = ui.render(output_frame)
        window.display(output_frame)

        if command is None:
            conn.sendall(bytes('p', "utf-8"))
        else:
            conn.sendall(bytes(command, "utf-8"))            