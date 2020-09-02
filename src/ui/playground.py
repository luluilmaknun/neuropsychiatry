# Import modules
import tkinter as tk
from math import sin, pi

from src.ui.box import Box
import src.constants as constants


class Playground(tk.Canvas):
    """
        The black canvas in the middle of main frame. Place where cursor and target moves
    """
    def __init__(self, root, *args, **kwargs):
        # Init playground canvas and set its size
        super().__init__(root, *args, **kwargs)
        self.pack(anchor=tk.CENTER, expand=True)
        self.height = kwargs['height']
        self.width = kwargs['width']
        self.center_y = self.height / 2
        self.center_x = self.width / 2
        self.STATIC_SIZE_H = 360

        self.score_label = self.create_text(
            [self.center_x, self.center_y],
            font=('Arial', 100, 'bold'),
            fill='lime green',
            text='0')
        self.hide_score()

        self.clock_freq = 50

    def create_boxes(self, size, target_opacity, cursor_opacity):
        """
            Create cursor and target in playground

            :param size: Defined the size of the cursor and target
            :param target_opacity: Defined the opacity of the cursor
            :param cursor_opacity: Defined the opacity of the target
        """
        self.size_cursor_target = size
        self.target = Box(self, 'red', size, target_opacity)
        self.cursor = Box(self, 'yellow', size, cursor_opacity)

        self.cursor.move(self.center_x - (size/2), self.center_y - (size/2))
        self.target.move(self.center_x - (size/2), self.center_y - (size/2))

    def destroy_boxes(self):
        """
            Remove cursor and target from playground
        """
        self.target.delete()
        self.cursor.delete()

    def move_target(self, amp, freq, pert_amp, pert_freq, phase_time):
        """
            Move the target sinusoindally based on the function parameters.
            The target's movement will be affected by perturbation based on the pert_amp and pert_freq

            :return position_data: Current perturbed position of target
        """
        # Calculate perturbed position
        position = amp * sin(2 * pi * freq * phase_time / self.clock_freq)
        perturbation = pert_amp * sin(2 * pi * pert_freq * phase_time / self.clock_freq)
        pos_y = position + perturbation
        position_data = pos_y

        # Move target's interface in playground
        pos_y = self.center_y - pos_y * constants.RADIUS - self.size_cursor_target/2
        self.target.move(0, pos_y)

        return position_data

    def move_cursor(self, cursor_pos_read_data, amp, freq, phase_time):
        """
            Move the cursor sinusoindally based on the perturbation parameters.

            :return position_data: Current perturbed position of cursor
            :return pert: Current perturbation of cursor
        """
        pert = amp * sin(2 * pi * freq * phase_time / self.clock_freq)
        pos_y = cursor_pos_read_data + pert
        position_data = pos_y

        # Move cursor's interface in playground
        pos_y = self.center_y - pos_y * constants.RADIUS - self.size_cursor_target/2
        self.cursor.move(0, pos_y)

        return position_data, pert

    def show_score(self, score):
        """
            Method to show score label in playground
        """
        self.itemconfig(self.score_label, text=str(score), state=tk.NORMAL)

    def hide_score(self):
        """
            Method to hide score label in playground
        """
        self.itemconfig(self.score_label, text='', state=tk.HIDDEN)

    def show_cursor(self):
        """
            Method to show cursor's interface in playground
        """
        self.cursor.show()

    def hide_cursor(self):
        """
            Method to hide cursor's interface in playground
        """
        self.cursor.hide()

    def show_target(self):
        """
            Method to show target's interface in playground
        """
        self.target.show()

    def hide_target(self):
        """
            Method to hide target's interface in playground
        """
        self.target.hide()
