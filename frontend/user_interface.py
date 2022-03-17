from distutils.log import debug
from email.policy import default
import cv2
import math
import numpy as np

class UserInterface:
    def __init__(
        self, 
        buttons, 
        screen_width=1920, 
        screen_height=1080, 
        default_command='h', 
        window_name='Wheelchair Interface', 
        debug_mode=False
    ):
        self.buttons = buttons
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.default_command = default_command
        self.window_name = window_name
        self.debug_mode = debug_mode

        cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        self.cursor_x = screen_width / 2
        self.cursor_y = screen_height / 2

        self.prev_command = default_command

        for i in range(len(buttons)):
            for j in range(len(buttons)):
                if i == j:
                    continue

                if buttons[i].is_overlapping(buttons[j]):
                    raise ValueError('Overlapping buttons are not allowed.')

    def update_cursor(self, x, y):
        self.cursor_x = int(x)
        self.cursor_y = int(y)

        command = None
        for button in self.buttons:
            if button.is_within(x, y):
                command = button.command
                break
            command = self.default_command
        
        if command == self.prev_command:
            command = None
        else:
            self.prev_command = command

        frame = self._blank_frame()
        if self.debug_mode:
            frame = cv2.putText(frame, self.prev_command.upper(), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2)
        self._render(frame)

    def _render(self, frame):
        for button in self.buttons:
            frame = button.render(frame)
        frame = self._render_cursor(frame)
        cv2.imshow(self.window_name, frame)
        self._wait(1)
        
    def _render_cursor(self, frame):
        return cv2.circle(frame, (int(self.cursor_x), int(self.cursor_y)), 25, (255, 0, 0), -1)

    def _wait(self, delay_ms):
        key = cv2.waitKey(delay_ms)
        # exit on escape key
        if key == 27:
            exit(0)

    def _blank_frame(self):
        frame = np.zeros([self.screen_height, self.screen_width, 3], dtype=np.uint8)
        frame.fill(255)
        return frame
