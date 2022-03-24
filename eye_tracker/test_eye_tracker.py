import sys

sys.path.append('..')

from eye_tracker import EyeTracker
from frontend.window import Window
from calibration_sequence import render_dot

window = Window('Test Eye Tracker')
eye_tracker = EyeTracker(window)
eye_tracker.calibrate()

while True:
    x, y = eye_tracker.get_cursor()
    window.display(render_dot(x, y, window.blank_frame()))

