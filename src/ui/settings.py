import tkinter as tk


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

        # Buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=3, column=0, padx=5, pady=12)

        self.save_button = tk.Button(self.button_frame, width=13, text="Save Changes",
                                     command=self.save_settings)
        self.save_button.grid(row=0, column=0, padx=5)

        self.save_button = tk.Button(self.button_frame, width=13, text="Close",
                                     command=self.close)
        self.save_button.grid(row=0, column=1, padx=5)

        self.configure_condition_table()

    def configure_condition_table(self):
        self.fields = ['Condition', 'Delay',
                       'Target Frequency',
                       'Cursor Pertubation Frequency',
                       'Target Pertubation Frequency',
                       'Target Amplitude',
                       'Cursor Perturbation Amplitude',
                       'Target Perturbation Amplitude',
                       'Visibility of Cursor',
                       'Visibility of Target',]
        self.fields_key = list(self.conditions[0].keys())
        self.num_of_conditions = len(self.conditions)

        for i in range(len(self.fields)):
            tk.Label(self.conditions_frame, text=self.fields[i], wraplength=70, width=9).grid(row=0, column=i, sticky=tk.W,
                                                                                              padx=5, pady=5)

        for i in range(self.num_of_conditions):
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

        for i in range(self.num_of_conditions):
            tk.Button(self.conditions_frame, text='x', command=(lambda: self.delete_condition(i + 1))) \
                .grid(row=i + 1, column= len(self.fields)+1, padx=10, ipadx=5)

    def save_settings(self):
        self.settings_dict['num_of_conditions'] = self.num_of_conditions
        self.settings_dict['length_of_trial'] = self.length_of_trial.get()
        self.settings_dict['size_cursor_target'] = self.size_cursor_target.get()
        self.settings_dict['num_of_trials'] = self.num_of_trials.get()

        self.conditions = []
        for i in range(self.num_of_conditions):
            self.conditions.append({})
            for j in range(len(self.fields_key)):
                if self.fields[j] == 'Condition':
                    self.conditions[i][self.fields_key[j]] = i + 1
                else:
                    self.conditions[i][self.fields_key[j]] = self.vals[i][j - 1].get()

        self.settings_dict['conditions'] = self.conditions

    def get_settings(self):
        return self.settings_dict

    def waiting(self):
        self.root.wait_window()
        return self.settings_dict

    def add_condition(self):
        self.num_of_conditions += 1
        self.vals.append([])

        for j in range(len(self.fields)):
            if self.fields[j] == 'Condition':
                ent = tk.Label(self.conditions_frame, text=self.num_of_conditions)
                ent.grid(row=self.num_of_conditions, column=j)
            else:
                val = tk.DoubleVar()
                ent = tk.Entry(self.conditions_frame, textvariable=val, width=8)
                ent.grid(row=self.num_of_conditions, column=j, pady=5)
                self.vals[self.num_of_conditions - 1].append(val)

        id = self.num_of_conditions
        tk.Button(self.conditions_frame, text='x', command=(lambda: self.delete_condition(id))) \
            .grid(row=self.num_of_conditions, column=len(self.fields) + 1, padx=10, ipadx=5)

    def delete_condition(self, row):
        l = list(self.conditions_frame.grid_slaves(row=self.num_of_conditions))
        self.num_of_conditions -= 1

        for r in range(row, self.num_of_conditions + 1):
            for c in range(len(self.fields_key)):
                self.vals[r-1][c-1].set(self.vals[r][c-1].get())

        del self.vals[-1]
        for w in l:
            w.destroy()

    def close(self):
        self.root.destroy()
