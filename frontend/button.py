import math
import cv2

D = 1
KX = 100
KY = 100
M = 1

DT = 0.1

AX = -(DT*KX)/M
AY = -(DT*KY)/M
B = (1 - (DT*D)/M)
C = DT/M

class Button:
    def __init__(self, screen_width, screen_height, x, y, radius, color, command):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = int(x * screen_width)
        self.y = int(y * screen_height)
        self.radius = int(radius * screen_width)
        self.color = color
        self.command = command
        self.fx = self.x * (KX / M) * M
        self.fy = self.y * (KY / M) * M
        self.prev_vx = 0
        self.prev_vy = 0

    def is_within(self, x, y):
        return math.dist([x, y], [self.x, self.y]) < self.radius

    def is_overlapping(self, other):
        return math.dist([self.x, self.y], [other.x, other.y]) < self.radius + other.radius

    def adjust_cursor(self, x, y):
        x = x + DT * self.prev_vx
        y = y + DT * self.prev_vy
        vx = AX * x + B * self.prev_vx + C * self.fx
        vy = AY * y + B * self.prev_vy + C * self.fy
        self.prev_vx = vx
        self.prev_vy = vy
        return x, y

    def render(self, frame):
        return cv2.circle(frame, (self.x, self.y), self.radius, self.color, 5)
