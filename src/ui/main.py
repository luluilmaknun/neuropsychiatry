import tkinter as tk
import tkinter.filedialog as tk_fd
from os.path import expanduser
import time
import nidaqmx
import numpy as np
import math
import src.constants as constants

from src.ui.settings import SettingsFrame
from src.ui.playground import Playground


class MainFrame(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, *kwargs)
        self.pack(anchor=tk.CENTER, fill=tk.Y)
        self.root = root
        self.root.title("Neuropsikiatri")

        # Init nidaqmx task variable
        self.is_zeroed = False  # button zero if clicked, unknown functionality?
        self.channel_zero_button_value = [0] * constants.CHANNEL_COUNT
        self.channel_read_value = [0] * constants.CHANNEL_COUNT

        # Init target variable
        self.target_position_data = 0
        self.is_target_moved = False

        # Init cursor variable
        self.cursor_position_data_buffer = [0] * constants.DELAY_BUFFER_LEN
        self.cursor_position_data = 0
        self.delay_pointer = 0   # what is this?
        self.pertubation = 0

        # Init scoring variable
        self.total_score = 0
        self.current_score = 0
        self.score_count = 0
        self.norm_score = 0

        # Init trial variable
        self.phase_time = 0
        self.current_phase = 0
        self.next_phase_time = 0
            #number_of_output_data = 9
            #output_data = [0] * number_of_output_data

        # Set MainFrame width and height based on screen size
        self.w = self.root.winfo_screenwidth()
        self.h = self.root.winfo_screenheight()
        self.root.geometry("%dx%d+0+0" % (self.w, self.h))

        # Default Settings Conditions on first open
        self.settings = {
            'num_of_conditions': 1,
            'num_of_trials': 10,
            'length_of_trial': 10,
            'size_cursor_target': 30,
            'conditions': [
                {
                    'condition': 1,
                    'delay': 0.5,
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
        self.init_playground(self.h * 0.8)
        self.update()

        # Init nidaqmx task
        self.nidaq_task = nidaqmx.task.Task("ReadVoltageTwoChannel")
        self.nidaq_task.ai_channels.add_ai_voltage_chan(
            "Dev1/ai0, Dev1/ai4",
            0,
            nidaqmx.constants.TerminalConfiguration.DIFFERENTIAL,
            constants.READ_DATA_MIN_VALUE,
            constants.READ_DATA_MAX_VALUE,
            nidaqmx.constants.VoltageUnits.VOLTS,
            0)
        self.nidaq_task.timing.cfg_samp_clk_timing(
            constants.READ_DATA_SAMPLE_RATE,
            0,
            nidaqmx.constants.Edge.RISING,
            nidaqmx.constants.AcquisitionType.CONTINUOUS,
            0)
        ConstantOverwrite = nidaqmx.constants.OverwriteMode
        self.nidaq_task.in_stream.over_write = ConstantOverwrite.OVERWRITE_UNREAD_SAMPLES
        self.nidaq_task.start()

        # Start the mainframe
        self.start()
    
    def init_new_phase(self):
        self.current_phase += 1
        if self.current_phase == constants.END_PHASE:
            self.current_phase = constants.START_PHASE
        self.phase_time = 0

        if self.current_phase == constants.START_PHASE:
            self.next_phase_time = 100 #temp
            # init trial
        elif self.current_phase == constants.TRACK_PHASE:
            self.is_target_moved == True
            # make something (in)visible
            self.next_phase_time = constants.TRACK_TIME * constants.CLOCK_FREQUENCY
        elif current_phase == constants.SCORE_PHASE:
            # make something (in)visible
            self.norm_score = int(1000 * self.total_score / self.score_count)
            # display score
            self.next_phase_time = 200
            # toneoff ?
        elif current_phase == constants.REST_PHASE:
            #display '+' character
            self.next_phase_time = 100

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
        self.playground = Playground(self.root, height=size, width=size, bg='black')
        self.playground.create_boxes(100)

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

    def run(self):
        data = self.nidaq_task.read(constants.READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH)
        self.channel_read_value[0] = sum(data[0])/constants.READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH
        self.channel_read_value[1] = sum(data[1])/constants.READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH

        # w['text'] = 'ai0: %.5f\nai4: %.5f' % (channel_read_value[0], channel_read_value[1])

        # One channel data processing
        self.cursor_position_data_buffer[self.delay_pointer] = (self.channel_read_value[0] - self.channel_zero_button_value[0]) * constants.CURSOR_SCALE - 1
        if not self.is_zeroed:
            self.channel_zero_button_value[0] = self.channel_read_value[0]
            self.is_zeroed = True

        self.cursor_position_data = self.cursor_position_data_buffer[((self.delay_pointer + constants.DELAY_BUFFER_LEN - self.settings['conditions']['delay'] * constants.CLOCK_FREQUENCY) % constants.DELAY_BUFFER_LEN)]
        if abs(self.cursor_position_data) > 2000:
            self.cursor_position_data = np.sign(self.cursor_position_data) * 2000
        self.phase_time += 1

        if self.phase_time == self.next_phase_time:
            self.init_new_phase()
            
        if self.is_target_moved:
            self.target_position_data = self.playground.move_target(1, 0.4, self.phase_time)
            
            self.cursor_position_data = self.playground.move_cursor(self.cursor_position_data, 1, 0.4, self.phase_time)

            self.current_score = math.exp(-abs(self.cursor_position_data - self.target_position_data) / constants.SCORE_CONST)
            self.score_count += 1
            self.total_score += self.current_score
        else:
            self.current_score = 0
            self.target_position_data = 0
        
        self.delay_pointer = (self.delay_pointer + 1) % constants.DELAY_BUFFER_LEN
        self.root.after(constants.WINDOW_REFRESH_TIME, self.run)

    def start(self):
        """
        for i in range(phase):
            self.playground.move_target(amp, freq, i+1)
            time.sleep(pause)   # Set time here
            self.update()
        """
        self.init_new_phase()
        self.run()


def main():
    root = tk.Tk()
    MainFrame(root)
    root.mainloop()


if __name__ == '__main__':
    main()
