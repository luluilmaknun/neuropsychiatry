import tkinter as tk
from src.ui.conditions import ConditionsFrame


class SettingsFrame(tk.Toplevel):
    def __init__(self, root, settings_dict):
        self.root = root
        self.root.title("Settings")
        self.settings_dict = settings_dict
        self.conditions = self.settings_dict['conditions']

        # Number of Conditions
        tk.Label(self.root, text="Number of Conditions").grid(row=0, column=0)
        self.num_of_conditions = tk.IntVar()
        self.num_of_conditions.set(self.settings_dict['num_of_conditions'])
        self.num_of_conditions_entry = tk.Spinbox(self.root, from_=0, to=20,
                                                  textvariable=self.num_of_conditions)
        self.num_of_conditions_entry.grid(row=0, column=1)

        # Length of trial
        tk.Label(self.root, text="Length of Trial").grid(row=1, column=0)
        self.length_of_trial = tk.IntVar()
        self.length_of_trial.set(self.settings_dict['length_of_trial'])
        self.length_of_trial_entry = tk.Spinbox(self.root,
                                                textvariable=self.length_of_trial)
        self.length_of_trial_entry.grid(row=1, column=1)

        # Size of cursor/target
        tk.Label(self.root, text="Size of Cursor/Target").grid(row=2, column=0)
        self.size_cursor_target = tk.IntVar()
        self.size_cursor_target.set(self.settings_dict['size_cursor_target'])
        self.size_cursor_target_entry = tk.Spinbox(self.root, from_=0, to=100,
                                                   textvariable=self.size_cursor_target)
        self.size_cursor_target_entry.grid(row=2, column=1)

        # Number of trials
        tk.Label(self.root, text="Number of Trials").grid(row=3, column=0)
        self.num_of_trials = tk.IntVar()
        self.num_of_trials.set(self.settings_dict['num_of_trials'])
        self.num_of_trials_entry = tk.Spinbox(self.root,
                                              textvariable=self.num_of_trials)
        self.num_of_trials_entry.grid(row=3, column=1)

        # save and set button
        self.set_button = tk.Button(self.root, text="Set Conditions",
                                    command=self.setting_conditions)
        self.save_button = tk.Button(self.root, text="Save Changes",
                                     command=self.save_settings)
        self.set_button.grid(row=4, column=0)
        self.save_button.grid(row=4, column=1)

    def setting_conditions(self):
        self.top_level = tk.Toplevel(self.root)
        self.conditions = ConditionsFrame(self.top_level,
                                          self.num_of_conditions,
                                          self.settings_dict['conditions']).waiting()
        print(self.conditions)

    def save_settings(self):
        self.settings_dict['num_of_conditions'] = self.num_of_conditions.get()
        self.settings_dict['length_of_trial'] = self.length_of_trial.get()
        self.settings_dict['size_cursor_target'] = self.size_cursor_target.get()
        self.settings_dict['num_of_trials'] = self.num_of_trials.get()
        self.settings_dict['conditions'] = self.conditions

    def get_settings(self):
        return self.settings_dict

    def waiting(self):
        self.root.wait_window()
        return self.settings_dict
