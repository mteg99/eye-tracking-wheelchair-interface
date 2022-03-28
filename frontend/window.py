import cv2
import pyautogui
import numpy as np

class Window:
    def __init__(self, name):
        self.name = name

        cv2.namedWindow(name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        self.cleanup_routines = []

    def display(self, frame, delay_ms=1):
        cv2.imshow(self.name, frame)
        key = cv2.waitKey(delay_ms)
        # exit on escape key
        if key == 27:
            cv2.destroyWindow(self.name)
            for routine in self.cleanup_routines:
                routine()
            exit(0)

    def blank_frame(self):
        screen_width, screen_height = pyautogui.size()
        frame = np.zeros([screen_height, screen_width, 3], dtype=np.uint8)
        frame.fill(255)
        return frame

    def add_cleanup_routine(self, routine):
        self.cleanup_routines.append(routine)
