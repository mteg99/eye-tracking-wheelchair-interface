import platform

from eye_tracker.eye_tracker import EyeTracker
from frontend.window import Window
from eye_tracker.calibration_sequence import render_dot

window = Window('Test Eye Tracker')
if platform.system() == 'Windows':
    eye_tracker = EyeTracker(window, use_mp=False)
else:
    eye_tracker = EyeTracker(window, use_mp=True)
eye_tracker.calibrate()

while True:
    x, y = eye_tracker.get_cursor()
    if x is None or y is None:
        continue
    window.display(render_dot(x, y, window.blank_frame()))

