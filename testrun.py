import cv2
import numpy as np
import pyautogui
import socket
import sys
import pickle
import struct

from bufferless_video_capture import VideoCapture

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
BUTTON_RADIUS = 150
TURN_COLOR = (0, 0, 255)
FORWARD_COLOR = (0, 255, 0)
VERTICAL_CENTER = 540
LEFT_BUTTON_CENTER = 635
GO_BUTTON_CENTER = 960
RIGHT_BUTTON_CENTER = 1285
BUTTONS = ["left", "go", "right"]

WINDOW_NAME = "Wheelchair Interface"

last_button = None

def initialize():
    # camera = VideoCapture(0)
    cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(WINDOW_NAME,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    #return camera

def check_cursor(currentX, currentY):
    if (currentX >= (LEFT_BUTTON_CENTER - BUTTON_RADIUS) and currentX <= (LEFT_BUTTON_CENTER + BUTTON_RADIUS) 
    and currentY >= (VERTICAL_CENTER - BUTTON_RADIUS) and currentY <= (VERTICAL_CENTER + BUTTON_RADIUS)):
            return 'l'
    elif (currentX >= (GO_BUTTON_CENTER - BUTTON_RADIUS) and currentX <= (GO_BUTTON_CENTER + BUTTON_RADIUS) 
    and currentY >= (VERTICAL_CENTER - BUTTON_RADIUS) and currentY <= (VERTICAL_CENTER + BUTTON_RADIUS)):
            return 'f'
    elif (currentX >= (RIGHT_BUTTON_CENTER - BUTTON_RADIUS) and currentX <= (RIGHT_BUTTON_CENTER + BUTTON_RADIUS) 
    and currentY >= (VERTICAL_CENTER - BUTTON_RADIUS) and currentY <= (VERTICAL_CENTER + BUTTON_RADIUS)):
            return 'r'
    else:
        return 'h'
        
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
    initialize()
    HOST, PORT = "192.168.4.1", 9999
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        while True:
            output_frame = blank_frame()
            output_frame = cv2.circle(output_frame, (LEFT_BUTTON_CENTER, VERTICAL_CENTER), BUTTON_RADIUS, TURN_COLOR, 5)
            output_frame = cv2.circle(output_frame, (GO_BUTTON_CENTER, VERTICAL_CENTER), BUTTON_RADIUS, FORWARD_COLOR, 5)
            output_frame = cv2.circle(output_frame, (RIGHT_BUTTON_CENTER, VERTICAL_CENTER), BUTTON_RADIUS, TURN_COLOR, 5)
            wait(1)
            cv2.imshow(WINDOW_NAME, output_frame)

            currentX, currentY  = pyautogui.position()
            button = check_cursor(currentX, currentY)
            print(button)
            if (last_button != button):
                sock.sendall(bytes(button + "\n", "utf-8"))
                received = str(sock.recv(1024), "utf-8")
                print(received)
                last_button = button

if __name__ == '__main__':
    main()