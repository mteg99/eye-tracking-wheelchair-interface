import cv2
import pyautogui
import numpy as np

class UserInterface:
    def __init__(
        self, 
        buttons,
        default_command='h',
        debug_mode=False
    ):
        self.buttons = buttons
        self.default_command = default_command
        self.debug_mode = debug_mode

        screen_width, screen_height = pyautogui.size()
        self.cursor_x = screen_width / 2
        self.cursor_y = screen_height / 2
        self.prev_command = default_command

        for i in range(len(buttons)):
            for j in range(len(buttons)):
                if i == j:
                    continue

                if buttons[i].is_overlapping(buttons[j]):
                    raise ValueError('Overlapping buttons are not allowed.')

    def render(self, frame):
        if self.debug_mode:
            frame = cv2.putText(frame, self.prev_command.upper(), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2)
        for button in self.buttons:
            frame = button.render(frame)
        frame = cv2.circle(frame, (int(self.cursor_x), int(self.cursor_y)), 25, (255, 0, 0), -1)
        return frame

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

        return command
