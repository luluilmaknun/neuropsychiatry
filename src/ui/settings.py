import tkinter as tk
from src.ui.conditions import ConditionsFrame


class SettingsFrame(tk.Toplevel):
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(self.root, width=360, height=360)
        self.root.title("Settings")

        # CONDITION
        lab = tk.Label(self.root, text="Number of Condition")
        self.ent = tk.Spinbox(self.root, from_=0, to=20)
        self.but = tk.Button(self.root, text="Set",
                             command=self.setting_conditions)
        lab.pack(side='left')
        self.ent.pack(side='left')
        self.but.pack(side='left')

    def setting_conditions(self):
        num_of_condition = int(self.ent.get())
        self.conditions_frame = tk.Toplevel(self.root)
        self.app = ConditionsFrame(self.conditions_frame,
                                   num_of_condition=num_of_condition)
