import pyglet
import pyautogui

from eye_tracker.pykalman.pykalman import KalmanFilter
from eye_tracker.GazeTracking.gaze_tracking import GazeTracking
from eye_tracker.calibration import Calibration, calibration_step, render_dot
from utils.bufferless_video_capture import BufferlessVideoCapture

class EyeTracker:
    def __init__(self, window, calibration_file=None, use_mp=True):
        self.window = window

        self.screen_width, self.screen_height = pyautogui.size()

        self.gaze_tracker = GazeTracking()
        self.camera = BufferlessVideoCapture(0, 800, 600, 30)
        self.calibration = Calibration(0.04, 8, 6, self.gaze_tracker, file_name=calibration_file, use_mp=use_mp)

    def __del__(self):
        self.calibration.__del__()

    def calibrate(self):
        self.window.display(render_dot(self.screen_width / 2, self.screen_height / 2, self.window.blank_frame()), 1000)

        clock = pyglet.clock.Clock()
        clock.schedule_interval(calibration_step, self.calibration.dt, self.calibration, self.camera, self.window)
        while not self.calibration.done:
            clock.tick()

        initial_state_mean = [
            self.screen_width / 2,
            self.screen_height / 2,
            0,
            0,
            0,
            0
        ]

        A, H, W, Q = self.calibration.get_kalman_parameters()

        self.kf = KalmanFilter(
            transition_matrices = A,
            observation_matrices = H,
            transition_covariance = W,
            observation_covariance= Q,
            initial_state_mean = initial_state_mean
        )

        measurements = self.calibration.get_measurements()
        means, covariances = self.kf.filter(measurements)
        self.mean = means[-1]
        self.covariance = covariances[-1]

    def get_cursor(self):
        if not self.calibration.done:
            raise Exception('Calibration must be done before get_cursor() is called.')
        frame = self.camera.read()
        self.gaze_tracker.refresh(frame)
        if not self.gaze_tracker.pupils_located:
            return None, None
        x = 1 - self.gaze_tracker.horizontal_ratio()
        y = self.gaze_tracker.vertical_ratio()
        x, y = self.calibration.transform(x, y)
        self.mean, self.covariance = self.kf.filter_update(self.mean, self.covariance, (x, y))
        x = int(self.mean[0])
        y = int(self.mean[1])
        return x, y