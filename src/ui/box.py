import tkinter as tk


class Box():
    def __init__(self, canvas, color, size):
        self.canvas = canvas
        self.size = size
        self.rectangle = self.canvas.create_rectangle(0, 0, 0+size, 0+size, fill=color)

    def move(self, x, y):
        cord_x = x - (self.size/2)
        cord_y = y - (self.size/2)
        self.canvas.move(self.rectangle, cord_x, cord_y)
