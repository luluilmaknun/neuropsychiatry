import tkinter as tk


class Box():
    def __init__(self, canvas, color, size):
        self.canvas = canvas
        self.size = size
        self.rectangle = self.canvas.create_rectangle(0, 0, 0+size, 0+size, fill=color)
        self.x = 0
        self.y = 0

    def move(self, x, y):
        # move in 1 dimension
        if x == 0:
            offset_x = 0
        else:
            offset_x = x - self.x

        if y == 0:
            offset_y = 0
        else:
            offset_y = y - self.y

        self.x = x
        self.y = y

        self.canvas.move(self.rectangle, offset_x, offset_y)

    def hide(self):
        self.canvas.itemconfig(self.rectangle, state=tk.HIDDEN)

    def show(self):
        self.canvas.itemconfig(self.rectangle, state=tk.NORMAL)
