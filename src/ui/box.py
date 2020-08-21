import tkinter as tk
from PIL import Image, ImageTk


class Box():
    def __init__(self, canvas, color, size, opacity):
        self.canvas = canvas
        self.size = size
        self.alpha = int(opacity * 255)
        fill = self.canvas.winfo_rgb(color) + (self.alpha,)
        self.image = ImageTk.PhotoImage(Image.new('RGBA', (size, size), fill))
        self.rectangle = self.canvas.create_image(0, 0, image=self.image, anchor='nw')
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

    def delete(self):
        self.canvas.delete(self.rectangle)
