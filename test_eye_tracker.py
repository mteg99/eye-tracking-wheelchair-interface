import sys

from numpy import False_

from eye_tracker.eye_tracker import EyeTracker
from frontend.window import Window
from eye_tracker.calibration import render_dot

collect_data = True
window = Window('Test Eye Tracker', 1920, 1080)
if len(sys.argv) > 1:
    eye_tracker = EyeTracker(window, collect_data=collect_data, calibration_file=sys.argv[1])
else:
    eye_tracker = EyeTracker(window)
window.add_cleanup_routine(eye_tracker.__del__)
eye_tracker.calibrate()

while True:
    x, y = eye_tracker.get_cursor()
    if x is None or y is None:
        continue
    window.display(render_dot(x, y, window.blank_frame()))
