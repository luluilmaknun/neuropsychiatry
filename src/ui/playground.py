import tkinter as tk

from src.ui.box import Box


class Playground(tk.Canvas):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.pack(anchor=tk.CENTER)
        self.height = kwargs['height']
        self.width = kwargs['width']
        self.center_y = (self.winfo_height()/2) * self.height
        self.center_x = (self.winfo_width()/2) * self.width

        self.cursor = Box(self, 'yellow', 100)
        self.target = Box(self, 'red', 100)

        self.cursor.move(self.center_x, self.center_y)
        self.target.move(self.center_x, self.center_y)
