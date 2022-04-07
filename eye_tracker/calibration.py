import os
import cv2
import math
import queue
import numpy as np
import pandas as pd
import multiprocessing as mp

class Calibration:
    def __init__(self, dt, period, total_loops, screen_width, screen_height, gaze_tracker, collect_data=True, file_name=None, use_mp=True):
        if not collect_data and not file_name:
            raise Exception('Calibration must either collect data or load data.')
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.collect_data = collect_data
        self.file_name = file_name
        self.use_mp = use_mp

        self.x_ratios = []
        self.y_ratios = []

        if self.file_name:
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calibration_data')
            if not os.path.exists(data_dir) or not os.path.isdir(data_dir):
                os.mkdir(data_dir)

            self.file_path = os.path.join(data_dir, self.file_name)
            if os.path.exists(self.file_path):
                self.file = pd.read_csv(self.file_path)
            elif not collect_data:
                raise Exception('File {} cannot be found.'.format(file_name))
        
        if collect_data:
            self.dt = dt
            self.gaze_tracker = gaze_tracker

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

            self.step = 0
            self.done = False

            if use_mp:
                self.ratio_buffer = mp.Queue()
                self.frame_buffer = mp.JoinableQueue()
                self.frame_readers = []
                for p in range(mp.cpu_count()):
                    self.frame_readers.append(mp.Process(target=self._read_frames, daemon=True))
                    self.frame_readers[p].start()
        else:
            self.done = True
            self.x = []
            self.y = []
            self.vx = []
            self.vy = []
            self.ax = []
            self.ay = []
            self._process_data()

    def __del__(self):
        if self.collect_data and self.file_name:
            self._save_data()

    def get_position(self):
        if not self.collect_data:
            raise Exception('Calibration is not setup to collect data.')

        x = self.x[self.step]
        y = self.y[self.step]
        return x, y

    def update(self, frame):
        if not self.collect_data:
            raise Exception('Calibration is not setup to collect data.')

        if self.done:
            print('WARNING: calibration sequence complete, frame not recorded.')
            return

        if self.use_mp:
            self.frame_buffer.put_nowait((self.step, frame))
        else:
            self.gaze_tracker.refresh(frame)
            if not self.gaze_tracker.pupils_located:
                self.x_ratios.append(None)
                self.y_ratios.append(None)
            else:
                # invert horizontal ratio to match pixel coordinate convention
                # i.e. we want a small horizontal ratio to map to the left side of the screen
                self.x_ratios.append(1 - self.gaze_tracker.horizontal_ratio())
                self.y_ratios.append(self.gaze_tracker.vertical_ratio())

        self.step += 1
        if self.step == self.total_steps:
            self.done = True
            if self.use_mp:
                self.frame_buffer.join()
                ratios = []
                while len(ratios) < self.total_steps:
                    try:
                        ratios.append(self.ratio_buffer.get_nowait())
                    except queue.Empty:
                        continue
                self._cleanup_frame_readers()
                ratios.sort()
                ratios = [r[1] for r in ratios]
                ratios = list(map(list, zip(*ratios)))
                self.x_ratios = ratios[0]
                self.y_ratios = ratios[1]
            self._fill_missing_ratios()
            self._process_data()

    def get_measurements(self):
        if self.collect_data and not self.done:
            raise Exception('Calibration must be done before get_measurements() is called.')
        return list(zip(self.x_measurements, self.y_measurements))

    def get_kalman_parameters(self):
        assert len(self.x_measurements) == len(self.y_measurements)
        Z = np.array([self.x_measurements, self.y_measurements])
        length = len(self.x_measurements)

        X = np.array([self.x, self.y, self.vx, self.vy, self.ax, self.ay])
        X1 = X[:, :-1]
        X2 = X[:, 1:]        

        A = np.dot(np.dot(X2, X1.T), np.linalg.inv(np.dot(X1, X1.T)))
        H = np.dot(np.dot(Z, X.T), np.linalg.inv(np.dot(X, X.T)))
        W = np.dot(np.subtract(X2, np.dot(A, X1)), np.subtract(X2, np.dot(A, X1)).T) / (length - 1)
        Q = np.dot(np.subtract(Z, np.dot(H, X)), np.subtract(Z, np.dot(H, X)).T) / (length)

        return A, H, W, Q

    def transform(self, x, y):
        if not self.done:
            raise Exception('Calibration must be done before transform() is called.')
        x = (x - self.x_min) / (self.x_max - self.x_min)
        y = (y - self.y_min) / (self.y_max - self.y_min)
        x = x * self.screen_width
        y = y * self.screen_height
        return x, y

    def _read_frames(self):
        while True:
            try:
                step, frame = self.frame_buffer.get_nowait()
                self.gaze_tracker.refresh(frame)
                if not self.gaze_tracker.pupils_located:
                    self.ratio_buffer.put_nowait((step, (None, None)))
                else:
                    # invert horizontal ratio to match pixel coordinate convention
                    # i.e. we want a small horizontal ratio to map to the left side of the screen
                    self.ratio_buffer.put_nowait((
                        step,
                        (1 - self.gaze_tracker.horizontal_ratio(),
                        self.gaze_tracker.vertical_ratio())
                    ))
                self.frame_buffer.task_done()
            except queue.Empty:
                continue
    
    def _process_data(self):
        if self.file_name and os.path.exists(self.file_path):
            self._load_data()
        self._set_bounds()
        self._transform_all()

    def _fill_missing_ratios(self):
        num_x_missing = 0
        num_y_missing = 0

        prev_x = self.screen_width / 2
        for r in range(len(self.x_ratios)):
            if self.x_ratios[r] is None:
                num_x_missing += 1
                self.x_ratios[r] = prev_x
            else:
                prev_x = self.x_ratios[r]

        prev_y = self.screen_height /2
        for r in range(len(self.y_ratios)):
            if self.y_ratios[r] is None:
                num_y_missing += 1
                self.y_ratios[r] = prev_y
            else:
                prev_y = self.y_ratios[r]

        print('x: {}/{}'.format(self.total_steps - num_x_missing, self.total_steps))
        print('y: {}/{}'.format(self.total_steps - num_y_missing, self.total_steps))

    def _load_data(self):
        self.x_ratios += self.file['x_ratios'].to_list()
        self.y_ratios += self.file['y_ratios'].to_list()
        self.x += self.file['x'].to_list()
        self.y += self.file['y'].to_list()
        self.vx += self.file['vx'].to_list()
        self.vy += self.file['vy'].to_list()
        self.ax += self.file['ax'].to_list()
        self.ay += self.file['ay'].to_list()

    def _set_bounds(self):
        self.x_min = np.nanmin(self.x_ratios)
        self.x_max = np.nanmax(self.x_ratios)
        self.y_min = np.nanmin(self.y_ratios)
        self.y_max = np.nanmax(self.y_ratios)

    def _transform_all(self):
        assert len(self.x_ratios) == len(self.y_ratios)
        length = len(self.x_ratios)
        self.x_measurements = [0] * length
        self.y_measurements = [0] * length
        for i in range(length):
            x, y = self.transform(self.x_ratios[i], self.y_ratios[i])
            self.x_measurements[i] = x
            self.y_measurements[i] = y

    def _save_data(self):
        if not self.done:
            print('WARNING: calibration interrupted, data not saved.')
            return

        while True:
            print('Save calibration data to file {}? [y/n]:'.format(self.file_name))
            i = str(input())
            if i == 'y':
                print('Saving data.')
                break
            if i == 'n':
                print('Data will not be saved.')
                return
        
        pd.DataFrame({
            'x_ratios': self.x_ratios,
            'y_ratios': self.y_ratios,
            'x': self.x,
            'y': self.y,
            'vx': self.vx,
            'vy': self.vy,
            'ax': self.ax,
            'ay': self.ay,
        }).to_csv(self.file_path)

    def _cleanup_frame_readers(self):
        if not self.use_mp:
            return

        for p in self.frame_readers:
            p.kill()
        self.frame_buffer.close()
        self.ratio_buffer.close()

def calibration_step(dt, sequence, camera, window):
    x, y = sequence.get_position()
    window.display(render_dot(x, y, window.blank_frame()))
    sequence.update(camera.read())

def render_dot(x, y, frame):
    return cv2.circle(frame, (int(x), int(y)), 25, (255, 0, 0), -1)
