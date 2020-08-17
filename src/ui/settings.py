import tkinter as tk
from src.ui.conditions import ConditionsFrame


class SettingsFrame(tk.Toplevel):
    def __init__(self, root, settings_dict):
        self.root = root
        self.root.title("Settings")
        self.settings_dict = settings_dict
        self.conditions = self.settings_dict['conditions']
        self.vals = []

        self.top_frame = tk.Frame(self.root)
        self.top_frame.grid(row=0, column=0, padx=5, pady=12, sticky=tk.W)

        self.btn_add_condition = tk.Button(self.root, text='Add Condition', command=self.add_condition)
        self.btn_add_condition.grid(row=1, column=0, sticky=tk.E, padx=15)

        self.conditions_frame = tk.Frame(self.root, highlightbackground='black', highlightthickness=1)
        self.conditions_frame.grid(row=2, column=0, padx=15, pady=12, ipady=10)

        # # Number of conditions
        # tk.Label(self.top_frame, text="Number of conditions", font=('Arial', 11)) \
        #     .grid(row=0, column=0, sticky=tk.W, padx=12, pady=(6, 0))
        # tk.Label(self.top_frame, text="(fill in with numbers)", font=('Arial', 8, 'italic')) \
        #     .grid(row=1, column=0, sticky=tk.W, padx=12, pady=(0, 6))
        # self.num_of_conditions = tk.IntVar()
        # self.num_of_conditions.set(self.settings_dict['num_of_conditions'])
        # self.num_of_conditions_entry = tk.Spinbox(self.top_frame, from_=0, to=20, font=("Arial", 18), width=5,
        #                                           textvariable=self.num_of_conditions)
        # self.num_of_conditions_entry.grid(row=0, rowspan=2, column=1, padx=5)

        # Length of trial
        tk.Label(self.top_frame, text="Length of Trial", font=('Arial', 11)) \
            .grid(row=2, column=0, sticky=tk.W, padx=12, pady=(6, 0))
        tk.Label(self.top_frame, text="(fill in with numbers in seconds)", font=('Arial', 8, 'italic')) \
            .grid(row=3, column=0, sticky=tk.W, padx=12, pady=(0, 6))
        self.length_of_trial = tk.IntVar()
        self.length_of_trial.set(self.settings_dict['length_of_trial'])
        self.length_of_trial_entry = tk.Spinbox(self.top_frame, from_=0, to=100, font=("Arial", 18), width=5,
                                                textvariable=self.length_of_trial)
        self.length_of_trial_entry.grid(row=2, rowspan=2, column=1, padx=5)

        # Size of cursor/target
        tk.Label(self.top_frame, text="Size of cursor/target", font=('Arial', 11)) \
            .grid(row=4, column=0, sticky=tk.W, padx=12, pady=(6, 0))
        tk.Label(self.top_frame, text="(fill in with numbers in percentage)", font=('Arial', 8, 'italic')) \
            .grid(row=5, column=0, sticky=tk.W, padx=12, pady=(0, 6))
        self.size_cursor_target = tk.IntVar()
        self.size_cursor_target.set(self.settings_dict['size_cursor_target'])
        self.size_cursor_target_entry = tk.Spinbox(self.top_frame, from_=0, to=100, font=("Arial", 18), width=5,
                                                   textvariable=self.size_cursor_target)
        self.size_cursor_target_entry.grid(row=4, rowspan=2, column=1, padx=5)

        # Number of trials
        tk.Label(self.top_frame, text="Number of trials per condition", font=('Arial', 11)) \
            .grid(row=6, column=0, sticky=tk.W, padx=12, pady=(6, 0))
        tk.Label(self.top_frame, text="(fill in with numbers)", font=('Arial', 8, 'italic')) \
            .grid(row=7, column=0, sticky=tk.W, padx=12, pady=(0, 6))
        self.num_of_trials = tk.IntVar()
        self.num_of_trials.set(self.settings_dict['num_of_trials'])
        self.num_of_trials_entry = tk.Spinbox(self.top_frame, from_=0, to=20, font=("Arial", 18), width=5,
                                              textvariable=self.num_of_trials)
        self.num_of_trials_entry.grid(row=6, rowspan=2, column=1, padx=5)

        # save and set button
        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=3, column=0, padx=5, pady=12)
        self.set_button = tk.Button(self.button_frame, text="Set Conditions",
                                    command=self.setting_conditions)
        self.save_button = tk.Button(self.button_frame, text="Save Changes",
                                     command=self.save_settings)
        self.set_button.grid(row=0, column=0, padx=5)
        self.save_button.grid(row=0, column=1, padx=5)

        self.configure_condition_table()

    def setting_conditions(self):
        self.top_level = tk.Toplevel(self.root)
        self.conditions = ConditionsFrame(self.top_level,
                                          self.num_of_conditions,
                                          self.settings_dict['conditions']).waiting()

    def configure_condition_table(self):
        self.fields = ['Condition', 'Delay',
                       'Cursor Frequency',
                       'Target Frequency',
                       'Cursor Perturbation Amplitude',
                       'Target Perturbation Amplitude',
                       'Visibility of Cursor',
                       'Visibility of Target',]
        self.fields_key = list(self.conditions[0].keys())

        for i in range(len(self.fields)):
            tk.Label(self.conditions_frame, text=self.fields[i], wraplength=70, width=9).grid(row=0, column=i, sticky=tk.W,
                                                                                              padx=5, pady=5)

        for i in range(len(self.conditions)):
            self.vals.append([])
            for j in range(len(self.fields)):
                if self.fields[j] == 'Condition':
                    ent = tk.Label(self.conditions_frame, text=i + 1)
                    ent.grid(row=i + 1, column=j)
                else:
                    val = tk.DoubleVar()
                    val.set(self.conditions[i][self.fields_key[j]])
                    ent = tk.Entry(self.conditions_frame, textvariable=val, width=8)
                    ent.grid(row=i + 1, column=j, pady=5)
                    self.vals[i].append(val)

    def save_settings(self):
        num_of_conditions = self.conditions_frame.grid_size()[1] - 1
        self.settings_dict['num_of_conditions'] = num_of_conditions
        self.settings_dict['length_of_trial'] = self.length_of_trial.get()
        self.settings_dict['size_cursor_target'] = self.size_cursor_target.get()
        self.settings_dict['num_of_trials'] = self.num_of_trials.get()

        conditions = []
        for i in range(num_of_conditions):
            conditions.append({})
            for j in range(len(self.fields_key)):
                if self.fields[j] == 'Condition':
                    conditions[i][self.fields_key[j]] = i + 1
                else:
                    conditions[i][self.fields_key[j]] = self.vals[i][j - 1].get()

        self.settings_dict['conditions'] = conditions

    def get_settings(self):
        return self.settings_dict

    def waiting(self):
        self.root.wait_window()
        return self.settings_dict

    def add_condition(self):
        return
