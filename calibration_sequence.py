import math
from re import X
import numpy as np

class CalibrationSequence:
    def __init__(self, dt, period, total_loops, screen_width, screen_height):
        self.step = 0

        self.dt = dt
        self.period = period
        self.screen_width = screen_width
        self.screen_height = screen_height

        steps_per_loop = int(period / dt)
        self.total_steps = steps_per_loop * total_loops * 2

        self.t = [(s + 1) * dt for s in range(self.total_steps)]
        def x(t): return (screen_width / 2) * math.sin(t * ((2 * math.pi) / period)) + (screen_width / 2)
        def y(t): return (screen_height / 2) * math.sin(t * ((2 * math.pi) / period)) + (screen_height / 2)
        def vx(t): return ((screen_width * math.pi) / period) * math.cos(t * ((2 * math.pi) / period))
        def vy(t): return ((screen_height * math.pi) / period) * math.cos(t * ((2 * math.pi) / period))
        def ax(t): return ((-2 * screen_width * (math.pi ** 2)) / (period ** 2)) * math.sin(t * ((2 * math.pi) / period))
        def ay(t): return ((-2 * screen_height * (math.pi ** 2)) / (period ** 2)) * math.sin(t * ((2 * math.pi) / period))

        self.x = [x(self.t[s]) if s < self.total_steps / 2 else (screen_width / 2) for s in range(self.total_steps)]
        self.y = [y(self.t[s]) if s >= self.total_steps / 2 else (screen_height / 2) for s in range(self.total_steps)]
        self.vx = [vx(self.t[s]) if s < self.total_steps / 2 else 0 for s in range(self.total_steps)]
        self.vy = [vy(self.t[s]) if s >= self.total_steps / 2 else 0 for s in range(self.total_steps)]
        self.ax = [ax(self.t[s]) if s < self.total_steps / 2 else 0 for s in range(self.total_steps)]
        self.ay = [ay(self.t[s]) if s >= self.total_steps / 2 else 0 for s in range(self.total_steps)]

        self.done = False
        self.x_measurements = []
        self.y_measurements = []

    def get_x(self):
        return self.x[self.step]

    def get_y(self):
        return self.y[self.step]

    def update(self, x_measurement, y_measurement):
        if self.done:
            print('WARNING: calibration sequence complete, measurement not recorded.')
            return

        self.x_measurements.append(x_measurement)
        self.y_measurements.append(y_measurement)

        self.step += 1
        if self.step == self.total_steps:
            self.done = True
            self._fill_missing_measurements()
            self._set_bounds()
            self._transform_all()

    def get_measurements(self):
        if not self.done:
            raise Exception('Calibration must be done before get_measurements() is called.')
        return list(zip(self.x_measurements, self.y_measurements))

    def get_kalman_parameters(self):
        X = np.array([self.x, self.y, self.vx, self.vy, self.ax, self.ay])
        X1 = X[:, :-1]
        X2 = X[:, 1:]

        Z = np.array([self.x_measurements, self.y_measurements])

        A = np.dot(np.dot(X2, X1.T), np.linalg.inv(np.dot(X1, X1.T)))
        H = np.dot(np.dot(Z, X.T), np.linalg.inv(np.dot(X, X.T)))
        W = np.dot(np.subtract(X2, np.dot(A, X1)), np.subtract(X2, np.dot(A, X1)).T) / (self.total_steps - 1)
        Q = np.dot(np.subtract(Z, np.dot(H, X)), np.subtract(Z, np.dot(H, X)).T) / (self.total_steps)

        return A, H, W, Q

    def transform(self, x, y):
        if not self.done:
            raise Exception('Calibration must be done before transform() is called.')
        x = (x - self.x_min) / (self.x_max - self.x_min)
        y = (y - self.y_min) / (self.y_max - self.y_min)
        x = x * self.screen_width
        y = y * self.screen_height
        return x, y

    def _fill_missing_measurements(self):
        prev_x = self.screen_width / 2
        for m in range(len(self.x_measurements)):
            if self.x_measurements[m] is None:
                self.x_measurements[m] = prev_x
            else:
                prev_x = self.x_measurements[m]

        prev_y = self.screen_height /2
        for m in range(len(self.y_measurements)):
            if self.y_measurements[m] is None:
                self.y_measurements[m] = prev_y
            else:
                prev_y = self.y_measurements[m]

    def _set_bounds(self):
        self.x_min = np.min(self.x_measurements)
        self.x_max = np.nanmax(self.x_measurements)
        self.y_min = np.nanmin(self.y_measurements)
        self.y_max = np.nanmax(self.y_measurements)

    def _transform_all(self):
        assert len(self.x_measurements) == len(self.y_measurements)
        for m in range(len(self.x_measurements)):
            x, y = self.transform(self.x_measurements[m], self.y_measurements[m])
            self.x_measurements[m] = x
            self.y_measurements[m] = y
