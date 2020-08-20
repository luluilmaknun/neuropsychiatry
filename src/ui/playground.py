import tkinter as tk
from math import sin, pi

from src.ui.box import Box
import src.constants as constants


class Playground(tk.Canvas):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.pack(anchor=tk.CENTER, expand=True)
        self.height = kwargs['height']
        self.width = kwargs['width']
        self.center_y = self.height / 2
        self.center_x = self.width / 2
        self.STATIC_SIZE_H = 360

        self.score_label = self.create_text([self.center_x, self.center_y], font=('Arial', 100, 'bold'), fill='lime green', text='0')
        self.hide_score()

        self.clock_freq = 50

    def create_boxes(self, size):
        self.size_cursor_target = size
        self.target = Box(self, 'red', size)
        self.cursor = Box(self, 'yellow', size)

        self.cursor.move(self.center_x - (size/2), self.center_y - (size/2))
        self.target.move(self.center_x - (size/2), self.center_y - (size/2))

    def move_target(self, amp, freq, phase_time):
        pos_y = amp * sin(2 * pi * freq * phase_time / self.clock_freq)
        position_data = pos_y

        pos_y = self.center_y - pos_y * constants.RADIUS - self.size_cursor_target/2

        self.target.move(0, pos_y)
        return position_data

    def move_cursor(self, cursor_pos_read_data, amp, freq, phase_time):
        pert = amp * sin(2 * pi * freq * phase_time / self.clock_freq)
        pos_y = cursor_pos_read_data + pert
        position_data = pos_y

        pos_y = self.center_y - pos_y * constants.RADIUS - self.size_cursor_target/2

        self.cursor.move(0, pos_y)
        return position_data, pert

    def show_score(self, score):
        self.itemconfig(self.score_label, text=str(score), state=tk.NORMAL)

    def hide_score(self):
        self.itemconfig(self.score_label, text='', state=tk.HIDDEN)

    def show_cursor(self):
        self.cursor.show()

    def hide_cursor(self):
        self.cursor.hide()

    def show_target(self):
        self.target.show()

    def hide_target(self):
        self.target.hide()

    def set_cursor_target_size(self, size):
        self.target.delete()
        self.cursor.delete()

        self.create_boxes(size)
