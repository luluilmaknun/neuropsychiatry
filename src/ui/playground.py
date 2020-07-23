import tkinter as tk
from math import sin, pi

from src.ui.box import Box


class Playground(tk.Canvas):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.pack(anchor=tk.CENTER)
        self.height = kwargs['height']
        self.width = kwargs['width']
        self.center_y = self.height / 2
        self.center_x = self.width / 2
        self.STATIC_SIZE_H = 360

        self.clock_freq = 50

    def create_boxes(self, size):
        self.size_cursor_target = size
        self.cursor = Box(self, 'yellow', size)
        self.target = Box(self, 'red', size)

        self.cursor.move(self.center_x - (size/2), self.center_y - (size/2))
        self.target.move(self.center_x - (size/2), self.center_y - (size/2))

    def move_target(self, amp, freq, phase_time):
        pos_y = amp * sin(2 * pi * freq * phase_time / self.clock_freq)
        if pos_y > 0:
            pos_y = pos_y * ((self.height / 2) - self.size_cursor_target)
        else:
            pos_y = pos_y * (self.height / 2)

        self.target.move(0, pos_y + self.center_y)
