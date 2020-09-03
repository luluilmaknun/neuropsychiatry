# Import modules
import json
import tkinter as tk
import tkinter.filedialog as tk_fd


class SettingsFrame(tk.Toplevel):
    """
        SettingsFrame contains all variables and functionalities to change settings
    """
    def __init__(self, root, settings_dict):
        # Init settings window
        self.root = root
        self.root.title("Settings")
        self.settings_dict = settings_dict
        self.conditions = self.settings_dict['conditions']
        self.vals = []  # 2D array contains conditions variables values

        # FRAMING
        self.top_frame = tk.Frame(self.root)
        self.top_frame.grid(row=0, column=0, padx=5, pady=12, sticky=tk.W)
        self.conditions_frame = tk.Frame(self.root, highlightbackground='black', highlightthickness=1)
        self.conditions_frame.grid(row=2, column=0, padx=15, pady=12, ipady=10)
        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=3, column=0, padx=5, pady=12)

        # Init Elements in Top Frames
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
        self.size_cursor_target_entry = tk.Spinbox(self.top_frame, from_=0, to=1000, font=("Arial", 18), width=5,
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

        # Init elements in button frame; export, import, save, close
        self.export_button = tk.Button(self.button_frame, width=13, text="Export Settings",
                                     command=self.export_settings)
        self.export_button.grid(row=0, column=0, padx=5)
        self.import_button = tk.Button(self.button_frame, width=13, text="Import Settings",
                                     command=self.import_settings)
        self.import_button.grid(row=0, column=1, padx=5)
        self.save_button = tk.Button(self.button_frame, width=13, text="Save Changes",
                                     command=self.save_settings)
        self.save_button.grid(row=0, column=2, padx=5)
        self.close_button = tk.Button(self.button_frame, width=13, text="Close",
                                     command=self.close)
        self.close_button.grid(row=0, column=3, padx=5)

        # Init elements in condition frame
        self.btn_add_condition = tk.Button(self.root, text='Add Condition', command=self.add_condition)
        self.btn_add_condition.grid(row=1, column=0, sticky=tk.E, padx=15)
        self.configure_condition_table()

    def configure_condition_table(self):
        """
            Method to configure condition table and load its values based on array self.condition
        """
        self.fields = ['Condition', 'Delay (s)',
                       'Target Frequency (Hz)',
                       'Cursor Pertubation Frequency (Hz)',
                       'Target Pertubation Frequency (Hz)',
                       'Target Amplitude',
                       'Cursor Perturbation Amplitude',
                       'Target Perturbation Amplitude',
                       'Visibility of Cursor',
                       'Visibility of Target',]
        self.fields_key = list(self.conditions[0].keys())
        self.num_of_conditions = len(self.conditions)

        # Set header row
        for i in range(len(self.fields)):
            tk.Label(self.conditions_frame, text=self.fields[i], wraplength=70, width=9) \
                .grid(row=0, column=i, sticky=tk.W, padx=5, pady=5)

        # Set condition tables values
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
                    self.vals[i].append(val)        # Store tables values in self.vals

        # Generate ordered number of condition
        for i in range(self.num_of_conditions):
            tk.Button(self.conditions_frame, text='x', command=(lambda: self.delete_condition(i + 1))) \
                .grid(row=i + 1, column= len(self.fields)+1, padx=10, ipadx=5)

    def save_settings(self):
        """
            Method for save current settings and store it in variable self.settings
        """
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
        """
            Method getter settings. Will return current saved settings
        """
        return self.settings_dict

    def waiting(self):
        """
            Keep the settings frame open until being destroyed/closed by user

            :return: current saved settings
        """
        self.root.wait_window()
        return self.settings_dict

    def add_condition(self):
        """
            Event handling for adding new condition row
        """
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
        """
            Event handling for removing selected row

            :param row: integer of intended row to be deleted
        """
        l = list(self.conditions_frame.grid_slaves(row=self.num_of_conditions))
        self.num_of_conditions -= 1

        for r in range(row, self.num_of_conditions + 1):
            for c in range(len(self.fields_key)):
                self.vals[r-1][c-1].set(self.vals[r][c-1].get())

        del self.vals[-1]
        for w in l:
            w.destroy()

    def import_settings(self):
        """
            Import chosen settings file in json
        """
        # Popup dialog, ask for json files
        filename = tk_fd.askopenfilename(defaultextension='.json', filetypes=[("json files", '*.json')],
                                         title="Choose filename")
        with open(filename, 'r') as f_im:
            settings_dict = json.load(f_im)

            self.num_of_conditions = settings_dict['num_of_conditions']
            self.length_of_trial.set(settings_dict['length_of_trial'])
            self.size_cursor_target.set(settings_dict['size_cursor_target'])
            self.num_of_trials.set(settings_dict['num_of_trials'])
            self.conditions = settings_dict['conditions']

            self.configure_condition_table()
            self.root.lift()

    def export_settings(self):
        """
            Export current saved settings in json
        """
        # Popup dialog, ask for target filename
        filename = tk_fd.asksaveasfilename(defaultextension='.json', filetypes=[("json files", '*.json')],
                                           title="Choose filename")
        with open(filename, 'w') as f_ex:
            self.save_settings()
            f_ex.write(json.dumps(self.settings_dict, indent=4))

    def close(self):
        """
            Destroy/Close settings frame/window
        """
        self.root.destroy()
