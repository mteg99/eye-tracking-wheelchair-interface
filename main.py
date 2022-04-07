import cv2
import math
import pyglet
import numpy as np
from datetime import datetime
import socket
import sys
import pickle
import struct
import pyautogui
import threading
from queue import Queue, Empty

from eye_tracker.eye_tracker import EyeTracker
from frontend.window import Window
from frontend.user_interface import UserInterface
from frontend.button import Button

SCREEN_WIDTH = 1920
SCREEN_HEIGHT  = 1080

window = Window('Wheelchair Interface', 1920, 1080)
output_frame = window.blank_frame()
frames = Queue()
commands = Queue()

def server_connection():
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
            frames.put(output_frame)

            try:
                command = commands.get_nowait()
            except:
                command = None
            
            if command is None:
                conn.sendall(bytes('p', "utf-8"))
            else:
                conn.sendall(bytes(command, "utf-8"))

COLLECT_DATA = False
if len(sys.argv) > 1:
    eye_tracker = EyeTracker(window, collect_data=COLLECT_DATA, calibration_file=sys.argv[1])
else:
    eye_tracker = EyeTracker(window, collect_data=COLLECT_DATA)
window.add_cleanup_routine(eye_tracker.__del__)
eye_tracker.calibrate()

forward = Button(SCREEN_WIDTH, SCREEN_HEIGHT, x=1/2, y=1/5, radius=1/10, color=(0, 255, 0), command='f')
left = Button(SCREEN_WIDTH, SCREEN_HEIGHT, x=1/8, y=1/2, radius=1/10, color=(0, 0, 255), command='l')
right = Button(SCREEN_WIDTH, SCREEN_HEIGHT, x=7/8, y=1/2, radius=1/10, color=(0, 0, 255), command='r')
ui = UserInterface([forward, left, right], debug_mode=True)

command = None
t = threading.Thread(target=server_connection)
t.daemon = True
t.start()

last_frame = window.blank_frame()
frame = window.blank_frame()
last_command = None

while True:
    x, y = eye_tracker.get_cursor()
    # x, y = pyautogui.position()
    if not x or not y:
        command = 'h'
    else:
        x_adjusted, y_adjusted = ui.adjust_cursor(x, y)
        if not x_adjusted or not y_adjusted:
            command = ui.get_command(x, y)
        else:
            eye_tracker.update_cursor(x_adjusted, y_adjusted)
            command = ui.get_command(x_adjusted, y_adjusted)

    if command != last_command:
        commands.put(command)
        last_command = command
    try:
        last_frame = frame
        frame = frames.get_nowait()   
    except Empty:
        frame = last_frame

    output_frame = ui.render(np.copy(frame))
    window.display(output_frame)
          