import math
import cv2

class Button:
    def __init__(self, x, y, radius, color, command):
        self.x = int(x)
        self.y = int(y)
        self.radius = int(radius)
        self.color = color
        self.command = command

    def is_within(self, x, y):
        return math.dist([x, y], [self.x, self.y]) < self.radius

    def is_overlapping(self, other):
        return math.dist([self.x, self.y], [other.x, other.y]) < self.radius + other.radius

    def render(self, frame):
        return cv2.circle(frame, (self.x, self.y), self.radius, self.color, -1)

