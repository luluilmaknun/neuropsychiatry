import tkinter as tk
import tkinter.filedialog as tk_fd
from os.path import expanduser

from src.ui.settings import SettingsFrame


class MainFrame(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, *kwargs)
        self.pack()
        self.root = root
        self.root.title("Neuropsikiatri")

        # Set MainFrame width and height based on screen size
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        self.root.geometry("%dx%d+0+0" % (w, h))

        # Default Settings Conditions on first open
        self.settings = {
            'num_of_conditions': 1,
            'num_of_trials': 10,
            'length_of_trial': 10,
            'size_cursor_target': 30,
            'conditions': [
                {
                    'condition': 1,
                    'delay': 100,
                    'perturbation': 5,
                    'cursor_pert_size': 5,
                    'target_pert_size': 5,
                    'visibility_cursor': 1,
                    'visibility_target': 0,
                }
            ],
        }

        # Init elements frame
        self.init_elements()
        self.init_playground(h)

    def init_elements(self):
        # FRAMING
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side='left', anchor=tk.W, padx=20, pady=20, fill=tk.BOTH, expand=True)
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side='right', anchor=tk.N, padx=20, pady=20, fill=tk.BOTH, expand=True)

        # BUTTON "Change Settings"
        self.btn_settings = tk.Button(self.left_frame, text="Change Settings",
                                      command=self.open_settings)
        self.btn_settings.pack(anchor=tk.NW)

        # SIDE PANEL
        # Record Icon
        tk.Label(self.right_frame, text="Recording", font=("Arial", 21)) \
            .grid(row=0, column=0, sticky=tk.NW, pady=20, padx=15)
        self.record_canvas = tk.Canvas(self.right_frame, width=60, height=60)
        self.record_canvas.grid(row=0, column=1)
        self.record_icon_out = self.record_canvas.create_oval(0, 0, 60, 60,
                                                              fill="red3", outline="red3")
        self.record_icon_in = self.record_canvas.create_oval(15, 15, 45, 45,
                                                             fill="red", outline="red")

        # Trial Counter
        tk.Label(self.right_frame, text="Trial counter", font=("Arial", 16)) \
            .grid(row=1, column=0, sticky=tk.NW, pady=15, padx=15)
        self.trial_counter = tk.IntVar()
        self.trial_counter.set(0)
        self.trial_counter_label = tk.Label(self.right_frame, textvariable=self.trial_counter,
                                            font=("Arial", 19))
        self.trial_counter_label.grid(row=1, column=1, sticky=tk.W)

        # Sample Counter
        tk.Label(self.right_frame, text="Sample counter", font=("Arial", 12)) \
            .grid(row=2, column=0, sticky=tk.NW, pady=15, padx=15)
        self.sample_counter = tk.IntVar()
        self.sample_counter.set(0)
        self.sample_counter_label = tk.Label(self.right_frame, textvariable=self.sample_counter,
                                             font=("Arial", 15))
        self.sample_counter_label.grid(row=2, column=1, sticky=tk.W)

        # BUTTON STOP & ZERO
        self.button_frame = tk.Frame(self.right_frame)
        self.button_frame.grid(columnspan=2, sticky=tk.E)
        tk.Button(self.button_frame, text="Stop", width=10, font=("Arial", 16)).pack(fill=tk.BOTH, expand=True)
        tk.Button(self.button_frame, text="Zero", width=10, font=("Arial", 16)).pack(fill=tk.BOTH, expand=True)

        # RADIOBUTTON RECORD
        self.record_flag = tk.BooleanVar()
        tk.Checkbutton(self.button_frame, text="Record", var=self.record_flag, font=("Arial", 16),
                       onvalue=True, offvalue=False).pack()

        # FILE MANAGER
        self.file_frame = tk.Frame(self.right_frame)
        self.file_frame.grid(columnspan=2, sticky=tk.E)
        self.record_dir = tk.StringVar()
        self.record_dir.set(expanduser("~"))
        self.record_dir_entry = tk.Entry(self.file_frame, font=("Arial", 12), width=25,
                                         textvariable=self.record_dir)
        self.record_dir_entry.pack()
        self.record_dir_entry.bind("<1>", self.change_dir)

        self.experiment_name = tk.StringVar()
        self.experiment_name_entry = tk.Entry(self.file_frame, font=("Arial", 12), width=18,
                                              textvariable=self.experiment_name)
        self.experiment_name_entry.pack(side='left', padx=2)

        self.experiment_number = tk.IntVar()
        self.experiment_number_entry = tk.Entry(self.file_frame, font=("Arial", 12), width=6,
                                                textvariable=self.experiment_number)
        self.experiment_number_entry.pack(side='left', padx=1)

    def init_playground(self, size):
        self.playground = tk.Canvas(self.root, height=size, width=size, bg='black')
        self.playground.pack(anchor=tk.CENTER)

    def increase_counter(self, counter='trial'):
        if counter == 'trial':
            self.trial_counter.set(self.trial_counter.get() + 1)
        elif counter == 'sample':
            self.sample_counter.set(self.sample_counter.get() + 1)

    def change_dir(self, event):
        self.record_dir.set(tk_fd.askdirectory())

    def open_settings(self):
        self.top_level = tk.Toplevel(self.root)
        self.settings = SettingsFrame(self.top_level, self.settings).waiting()
        print(self.settings)



def main():
    root = tk.Tk()
    MainFrame(root)
    root.mainloop()


if __name__ == '__main__':
    main()
