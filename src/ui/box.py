"""
    Box module
"""
import tkinter as tk
from PIL import Image, ImageTk


class Box():
    """
        Box class
    """
    def __init__(self, canvas, color, size, opacity):
        self.canvas = canvas
        self.size = size
        self.alpha = int(opacity * 255)
        fill = self.canvas.winfo_rgb(color) + (self.alpha,)
        self.image = ImageTk.PhotoImage(Image.new('RGBA', (size, size), fill))
        self.rectangle = self.canvas.create_image(
            0,
            0,
            image=self.image,
            anchor='nw')
        self.x_pos = 0
        self.y_pos = 0

    def move(self, x_arg, y_arg):
        """
            Method to move box
        """
        # move in 1 dimension
        if x_arg == 0:
            offset_x = 0
        else:
            offset_x = x_arg - self.x_pos

        if y_arg == 0:
            offset_y = 0
        else:
            offset_y = y_arg - self.y_pos

        self.x_pos = x_arg
        self.y_pos = y_arg

        self.canvas.move(self.rectangle, offset_x, offset_y)

    def hide(self):
        """
            Method to hide box
        """
        self.canvas.itemconfig(self.rectangle, state=tk.HIDDEN)

    def show(self):
        """
            Method to show box
        """
        self.canvas.itemconfig(self.rectangle, state=tk.NORMAL)

    def delete(self):
        """
            Method to delete box
        """
        self.canvas.delete(self.rectangle)
