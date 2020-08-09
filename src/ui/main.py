import tkinter as tk
import tkinter.filedialog as tk_fd
from os.path import expanduser
import time
import nidaqmx
import numpy as np
import math
import constants as constants

from settings import SettingsFrame
from playground import Playground


class MainFrame(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, *kwargs)
        self.pack(anchor=tk.CENTER, fill=tk.Y)
        self.root = root
        self.root.title("Neuropsikiatri")
        self._job = None
        self.init_running_variable()
        self.wtext = tk.Label(self.root)
        self.wtext.pack()

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
            0.15,#constants.READ_DATA_MIN_VALUE,
            0.2,#constants.READ_DATA_MAX_VALUE,
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

    def init_new_phase(self):
        self.current_phase += 1
        if self.current_phase == constants.END_PHASE:
            self.trial_number += 1
            if self.trial_number > self.settings['num_of_trials']:
                self.stop()
                return
            self.current_phase = constants.START_PHASE
        self.phase_time = 0
        self.wtext['text'] = 'trial: %.1d\nconditions: %.1d\nphase: %.1d' % (self.trial_number, self.list_counter, self.current_phase)

        if self.current_phase == constants.START_PHASE:
            self.list_counter += 1
            if self.list_counter >= self.settings['num_of_conditions']:
                self.list_counter = 0
            self.next_phase_time = 100
            self.score_count = 0
            self.current_score = 0
            self.norm_score = 0
            self.total_score = 0
            self.is_target_moved = False
            # update trial number display
        elif self.current_phase == constants.TRACK_PHASE:
            self.is_target_moved = True
            self.next_phase_time = self.settings['length_of_trial'] * 1000 / constants.CLOCK_FREQUENCY
        elif self.current_phase == constants.SCORE_PHASE:
            self.norm_score = int(1000 * self.total_score / self.score_count)
            # display score
            self.next_phase_time = 200
        elif self.current_phase == constants.REST_PHASE:
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
        self.start_stop_button = tk.Button(self.button_frame, text="Start", width=10, font=("Arial", 16), command=self.start)
        self.start_stop_button.pack(fill=tk.BOTH, expand=True)
        self.zero_button = tk.Button(self.button_frame, text="Zero", width=10, font=("Arial", 16), command=self.zero_pressed)
        self.zero_button.pack(fill=tk.BOTH, expand=True)

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
        data_dump = self.nidaq_task.read(100)
        self.channel_read_value[0] = sum(data[0])/constants.READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH
        self.channel_read_value[1] = sum(data[1])/constants.READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH

        # One channel data processing
        self.cursor_position_data_buffer[self.delay_pointer] = (self.channel_read_value[0] - self.channel_zero_button_value[0]) * constants.CURSOR_SCALE - 1
        if not self.is_zeroed:
            self.channel_zero_button_value[0] = self.channel_read_value[0]
            self.is_zeroed = True

        self.cursor_position_data = self.cursor_position_data_buffer[round((self.delay_pointer + constants.DELAY_BUFFER_LEN - self.settings['conditions'][self.list_counter]['delay'] * constants.CLOCK_FREQUENCY) % constants.DELAY_BUFFER_LEN)]
        if abs(self.cursor_position_data) > 2000:
            self.cursor_position_data = np.sign(self.cursor_position_data) * 2000
        self.phase_time += 1

        if self.phase_time == self.next_phase_time:
            self.init_new_phase()

        if self.is_target_moved:
            self.target_position_data = self.playground.move_target(1, 0.4, self.phase_time) #
            
            self.cursor_position_data = self.playground.move_cursor(self.cursor_position_data, 1, 0.4, self.phase_time)

            self.current_score = math.exp(-abs(self.cursor_position_data - self.target_position_data) / constants.SCORE_CONST)
            self.score_count += 1
            self.total_score += self.current_score
        else:
            self.current_score = 0
            self.target_position_data = 0
        
        self.delay_pointer = (self.delay_pointer + 1) % constants.DELAY_BUFFER_LEN
        self._job = self.root.after(20, self.run)

    def start(self):
        self.playground.move_target(0, 0, self.phase_time)
        self.playground.move_cursor(self.cursor_position_data, 0, 0, self.phase_time)
        self.start_stop_button['text'] = "Stop"
        self.start_stop_button['command'] = self.stop
        self.nidaq_task.start()
        self.init_new_phase()
        self.run()

    def stop(self):
        self.start_stop_button['text'] = "Start"
        self.start_stop_button['command'] = self.start
        self.nidaq_task.stop()
        self.init_running_variable()
    
    def zero_pressed(self):
        self.channel_zero_button_value[0] = self.channel_read_value[0]
        self.is_zeroed = True

    def init_running_variable(self):
        # Init nidaqmx task variable
        self.is_zeroed = False
        self.channel_zero_button_value = [0] * constants.CHANNEL_COUNT
        self.channel_read_value = [0] * constants.CHANNEL_COUNT

        # Init target variable
        self.target_position_data = 0
        self.is_target_moved = False

        # Init cursor variable
        self.cursor_position_data_buffer = [0] * constants.DELAY_BUFFER_LEN
        self.cursor_position_data = 0
        self.delay_pointer = 0
        self.pertubation = 0

        # Init scoring variable
        self.total_score = 0
        self.current_score = 0
        self.score_count = 0
        self.norm_score = 0

        # Init trial variable
        self.list_counter = -1
        self.trial_number = 0
        self.phase_time = 0
        self.current_phase = 0
        self.next_phase_time = 0
        if self._job is not None:
            self.root.after_cancel(self._job)
            self._job = None


def main():
    root = tk.Tk()
    MainFrame(root)
    root.mainloop()


if __name__ == '__main__':
    main()
