import math
import numpy as np

class CalibrationSequence:
    def __init__(self, dt, period, total_loops, screen_width, screen_height):
        self.step = 0
        self.loop_count = 0

        self.dt = dt
        self.period = period
        self.total_loops = total_loops
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.done = False
        self.horizontal = True
        self.total_steps = int(self.period / self.dt)
        self.t = [(s + 1) * self.dt for s in range(self.total_steps)]
        self.x = [(screen_width / 2) * math.sin(t * ((2 * math.pi) / self.period)) + (screen_width / 2) for t in self.t]
        self.y = [(screen_height / 2) * math.sin(t * ((2 * math.pi) / self.period)) + (screen_height / 2) for t in self.t]        

        self.measurements = []

    def get_x(self):
        if self.horizontal:
            return self.x[self.step]
        else:
            return self.screen_width / 2

    def get_y(self):
        if self.horizontal:
            return self.screen_height / 2
        else:
            return self.y[self.step]

    def update(self, measurment):
        if self.done:
            print('WARNING: calibration sequence complete, measurement not recorded.')
            return

        self.step += 1
        if self.step == self.total_steps:
            self.step = 0
            self.loop_count += 1
            if self.loop_count == self.total_loops:
                self.loop_count = 0
                if self.horizontal:
                    self.horizontal = False
                else:
                    self.done = True
                    self._set_bounds()
                    self._transform_all()
                    self._mask_missing_measurements()
                    return
        self.measurements.append(measurment)

    def get_measurements(self):
        if not self.done:
            raise Exception('Calibration must be done before get_measurements() is called.')
        return self.measurements

    def transform(self, x, y):
        if not self.done:
            raise Exception('Calibration must be done before transform() is called.')
        x = (x - self.x_min) / (self.x_max - self.x_min)
        y = (y - self.y_min) / (self.y_max - self.y_min)
        x = x * self.screen_width
        y = y * self.screen_height
        return x, y

    def _set_bounds(self):
        self.measurements = np.asarray(self.measurements, dtype=np.single)
        x = self.measurements[:,0]
        self.x_min = np.nanmin(x)
        self.x_max = np.nanmax(x)
        y = self.measurements[:,1]
        self.y_min = np.nanmin(y)
        self.y_max = np.nanmax(y)

    def _transform_all(self):
        for r in range(self.measurements.shape[0]):
            x, y = self.transform(self.measurements[r][0], self.measurements[r][1])
            self.measurements[r][0] = x
            self.measurements[r][1] = y

    def _mask_missing_measurements(self):
        shape = self.measurements.shape
        mask = np.zeros(shape)
        for r, c in [(r, c) for r in range(shape[0]) for c in range(shape[1])]:
            if np.isnan(self.measurements[r][c]):
                mask[r][c] = 1
        self.measurements = np.ma.array(self.measurements, dtype=np.single, mask=mask)
