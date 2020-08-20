import tkinter as tk
import tkinter.filedialog as tk_fd
import os
import nidaqmx
import src.constants as constants
from math import exp
from numpy import sign
from csv import writer

from src.ui.settings import SettingsFrame
from src.ui.playground import Playground


class MainFrame(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, *kwargs)
        self.pack(anchor=tk.CENTER, fill=tk.Y)
        self.root = root
        self.root.title("Neuropsikiatri")
        self._job = None
        self.init_running_variable()

        # Set MainFrame width and height based on screen size
        self.w = self.root.winfo_screenwidth()
        self.h = 900
        self.root.geometry("%dx%d+0+0" % (self.w, self.h))

        # Default Settings Conditions on first open
        self.settings = {
            'num_of_conditions': 1,
            'num_of_trials': 10,
            'length_of_trial': 10,
            'size_cursor_target': 100,
            'conditions': [
                {
                    'condition': 1,
                    'delay': 0,
                    'cursor_freq': 0.2,
                    'target_freq': 0.5,
                    'cursor_amp': 1,
                    'target_amp': 1,
                    'visibility_cursor': 1,
                    'visibility_target': 1,
                },
            ],
        }

        # Init elements frame
        self.init_elements()
        self.init_playground()
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

    def set_visibility(self, cursor_vb, target_vb):
        cursor_vb_settings = self.settings['conditions'][self.list_counter]['visibility_cursor']
        target_vb_settings = self.settings['conditions'][self.list_counter]['visibility_target']

        if cursor_vb and cursor_vb_settings:
            self.playground.show_cursor()
        else:
            self.playground.hide_cursor()

        if target_vb and target_vb_settings:
            self.playground.show_target()
        else:
            self.playground.hide_target()

    def init_new_phase(self):
        self.current_phase += 1
        if self.current_phase == constants.END_PHASE:
            self.current_phase = constants.START_PHASE
        self.phase_time = 0

        if self.current_phase == constants.START_PHASE:
            self.cursor_position_data_buffer = [0] * constants.DELAY_BUFFER_LEN
            self.cursor_position_data = 0
            self.target_position_data = 0
            self.channel_zero_button_value[0] = 0
            self.is_zeroed = False
            self.playground.move_cursor(self.cursor_position_data, 0, 0, self.phase_time)
            self.playground.move_target(0, 0, self.phase_time)
            self.delay_pointer = 0
            self.set_visibility(True, True)
            self.playground.hide_score()
            self.list_counter += 1
            if self.list_counter >= self.settings['num_of_conditions']:
                self.list_counter = 0
            self.next_phase_time = 100
            self.score_count = 0
            self.current_score = 0
            self.norm_score = 0
            self.total_score = 0
            self.is_target_moved = False
            self.trial_counter.set(self.trial_counter.get() + 1)

            # Set Current Conditions
            self.delay = self.settings['conditions'][self.list_counter]['delay']
            self.cursor_amp = self.settings['conditions'][self.list_counter]['cursor_amp']
            self.target_amp = self.settings['conditions'][self.list_counter]['target_amp']
            self.cursor_freq = self.settings['conditions'][self.list_counter]['cursor_freq']
            self.target_freq = self.settings['conditions'][self.list_counter]['target_freq']
        elif self.current_phase == constants.TRACK_PHASE:
            self.is_target_moved = True
            self.set_visibility(True, True)
            self.playground.hide_score()
            self.next_phase_time = self.settings['length_of_trial'] * constants.CLOCK_FREQUENCY
        elif self.current_phase == constants.SCORE_PHASE:
            self.set_visibility(False, False)
            self.is_target_moved = False
            self.norm_score = int(1000 * self.total_score / self.score_count)
            self.playground.show_score(self.norm_score)
            self.next_phase_time = 200
        elif self.current_phase == constants.REST_PHASE:
            self.playground.show_score('+')
            self.next_phase_time = 100

    def init_elements(self):
        # FRAMING
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side='left', anchor=tk.CENTER, padx=20, pady=20, fill=tk.Y, expand=True)
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side='right', anchor=tk.CENTER, padx=20, pady=20, fill=tk.Y, expand=True)

        # BUTTON "Change Settings"
        self.btn_settings = tk.Button(self.left_frame, text="Change Settings",
                                      command=self.open_settings)
        self.btn_settings.pack(anchor=tk.NW)

        self.canvas_text = tk.Label(self.left_frame)
        self.canvas_text.pack()

        # SIDE PANEL
        # Record Icon
        tk.Label(self.right_frame, text="Recording", font=("Arial", 21)) \
            .grid(row=0, column=0, sticky=tk.NW, pady=20, padx=15)
        self.record_canvas = tk.Canvas(self.right_frame, width=60, height=60)
        self.record_canvas.grid(row=0, column=1)
        self.record_icon = self.record_canvas.create_oval(2, 2, 60, 60,
                                                          fill="red3", outline="")

        # Trial Counter
        tk.Label(self.right_frame, text="Trial counter", font=("Arial", 16)) \
            .grid(row=1, column=0, sticky=tk.NW, pady=15, padx=15)
        self.trial_counter = tk.IntVar()
        self.trial_counter.set(0)
        self.trial_counter_label = tk.Label(self.right_frame, textvariable=self.trial_counter,
                                            font=("Arial", 22, 'bold'), fg='blue')
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
        self.button_frame.grid(columnspan=2, sticky=tk.NSEW, pady=65)
        self.start_stop_button = tk.Button(self.button_frame, text="Start", width=10, font=("Arial", 16), command=self.start)
        self.start_stop_button.pack(fill=tk.BOTH, expand=True, pady=8)
        self.zero_button = tk.Button(self.button_frame, text="Zero", width=10, font=("Arial", 16), command=self.zero_pressed)
        self.zero_button.pack(fill=tk.BOTH, expand=True, pady=8)

        # RADIOBUTTON RECORD
        self.record_on = tk.BooleanVar()
        tk.Checkbutton(self.button_frame, text="Record", var=self.record_on, font=("Arial", 16),
                       onvalue=True, offvalue=False).pack()

        # FILE MANAGER
        self.file_frame = tk.Frame(self.right_frame)
        self.file_frame.grid(columnspan=2, sticky=tk.E)
        self.record_dir = tk.StringVar()
        self.record_dir.set(os.path.expanduser("~"))
        self.record_dir_entry = tk.Entry(self.file_frame, font=("Arial", 14), width=22,
                                         textvariable=self.record_dir)
        self.record_dir_entry.pack(pady=4, ipadx=2, ipady=2, anchor=tk.CENTER)
        self.record_dir_entry.bind("<1>", self.change_dir)

        self.record_name = tk.StringVar(value='test')
        self.record_name_entry = tk.Entry(self.file_frame, font=("Arial", 14), width=16,
                                              textvariable=self.record_name)
        self.record_name_entry.pack(side='left', padx=2, ipadx=2, ipady=2, anchor=tk.CENTER)

        self.record_number = tk.IntVar(value=1)
        self.record_number_entry = tk.Entry(self.file_frame, font=("Arial", 14), width=5,
                                                textvariable=self.record_number)
        self.record_number_entry.pack(side='left', padx=2, ipadx=2, ipady=2, anchor=tk.CENTER)

    def init_playground(self):
        self.playground = Playground(self.root, height=constants.WINDOW_HEIGHT, width=constants.WINDOW_WIDTH, bg='black')
        self.playground.create_boxes(constants.CURSOR_SCALE)

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
        self.playground.set_cursor_target_size(self.settings['size_cursor_target'])

    def run(self):
        self.data = self.nidaq_task.read(constants.READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH)
        self.channel_read_value[0] = sum(self.data[0])/constants.READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH
        self.channel_read_value[1] = sum(self.data[1])/constants.READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH

        # One channel data processing
        cur_data = (self.channel_read_value[0] - self.channel_zero_button_value[0]) * constants.CURSOR_SCALE - 1
        self.cursor_position_data_buffer[self.delay_pointer] = cur_data
        if not self.is_zeroed:
            self.channel_zero_button_value[0] = self.channel_read_value[0]
            self.is_zeroed = True

        cur_data_id = round((self.delay_pointer + constants.DELAY_BUFFER_LEN - self.delay * constants.CLOCK_FREQUENCY) %
                            constants.DELAY_BUFFER_LEN)
        self.cursor_position_data = self.cursor_position_data_buffer[cur_data_id]
        if abs(self.cursor_position_data) > 2000:
            self.cursor_position_data = sign(self.cursor_position_data) * 2000
        self.phase_time += 1

        if self.phase_time == self.next_phase_time:
            self.init_new_phase()
        
        if self.trial_counter.get() > self.settings['num_of_trials']:
            self.stop()
            return

        if self.current_phase == constants.START_PHASE or self.current_phase == constants.TRACK_PHASE:
            self.cursor_position_data, self.perturbation = self.playground.move_cursor(self.cursor_position_data,
                                                                                       self.cursor_amp,
                                                                                       self.cursor_freq,
                                                                                       self.phase_time)
        if self.is_target_moved:
            self.target_position_data = self.playground.move_target(self.target_amp, self.target_freq, self.phase_time)

            self.current_score = exp(-abs(self.cursor_position_data - self.target_position_data) / constants.SCORE_CONST)
            self.score_count += 1
            self.total_score += self.current_score
        else:
            self.current_score = 0
            self.target_position_data = 0

        self.create_output_data()

        self.delay_pointer = (self.delay_pointer + 1) % constants.DELAY_BUFFER_LEN
        self._job = self.root.after(constants.WINDOW_REFRESH_TIME, self.run)

    def start(self):
        self.playground.move_target(0, 0, self.phase_time)
        self.playground.move_cursor(0, 0, 0, self.phase_time)

        waserror = False
        if self.record_on.get():
            record_dir = self.record_dir.get()
            record_name = self.record_name.get()
            record_number = self.record_number.get()

            if not os.path.isdir(record_dir):
                os.makedirs(record_dir)
            root = record_dir + "\\" + record_name
            waserror = False

            try:
                # Create files
                fn_hi = root + "hi-" + str(record_number) + '.csv'
                self.fid_hi = open(fn_hi, 'w')
                self.fwriter_hi = writer(self.fid_hi)

                fn_lo = root + "lo-" + str(record_number) + '.csv'
                self.fid_lo = open(fn_lo, 'w')
                self.fwriter_lo = writer(self.fid_lo)

                header = ['cursor position', 'target position', 'perturbation', 'current phase', 'condition',
                          'total score', 'score count', 'current score', 'samples read']
                self.fwriter_lo.writerow(header)
            except IOError as e:
                waserror = True
                self.messagebox.showerror(title='I/O Error', message=str(e))

            if not waserror:
                self.record_canvas.itemconfig(self.record_icon, fill='lime green')

        if not waserror:
            self.start_stop_button['text'] = "Stop"
            self.start_stop_button['command'] = self.stop
            self.record_dir_entry['state'] = 'disabled'
            self.record_name_entry['state'] = 'disabled'
            self.record_number_entry['state'] = 'disabled'

            self.trial_counter.set(0)
            self.current_phase = 0

            self.nidaq_task.start()
            self.init_new_phase()
            self.run()

    def stop(self):
        self.start_stop_button['text'] = "Start"
        self.start_stop_button['command'] = self.start
        self.record_dir_entry['state'] = 'normal'
        self.record_name_entry['state'] = 'normal'
        self.record_number_entry['state'] = 'normal'
        self.nidaq_task.stop()

        if self.record_on.get():
            try:
                # Write data on files
                data = [[int(x * 100) for x in single_ch] for single_ch in self.data]

                self.fwriter_lo.writerow(self.output_data)
                self.fwriter_hi.writerow(data)
            finally:
                self.fid_lo.close()
                self.fid_hi.close()

                # Change record icon and increase record number
                current_id = self.record_number.get()
                self.record_number.set(current_id + 1)
                self.record_canvas.itemconfig(self.record_icon, fill='red3')

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
        self.perturbation = 0

        # Init scoring variable
        self.total_score = 0
        self.current_score = 0
        self.score_count = 0
        self.norm_score = 0

        # Init trial variable
        self.list_counter = -1
        self.phase_time = 0
        self.current_phase = 0
        self.next_phase_time = 0

        # Init record data variable
        self.data = [[]] * constants.CHANNEL_COUNT
        self.output_data = [0] * constants.NUM_LO

        if self._job is not None:
            self.root.after_cancel(self._job)
            self._job = None

    def zero_pressed(self):
        self.channel_zero_button_value[0] = self.channel_read_value[0]
        self.is_zeroed = True

    def create_output_data(self):
        # data output record
        self.output_data[0] = int(self.cursor_position_data * 500)
        self.output_data[1] = int(self.target_position_data * 500)
        self.output_data[2] = int(self.perturbation * 500)
        self.output_data[3] = self.current_phase
        self.output_data[4] = self.list_counter + 1
        self.output_data[5] = int(self.total_score)
        self.output_data[6] = self.score_count
        self.output_data[7] = int(self.current_score * 1000)
        self.output_data[8] = constants.READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH

        if self.record_on.get():
            # Write data on files
            data = [[int(x * 100) for x in single_ch] for single_ch in self.data]
            self.fwriter_lo.writerow(self.output_data)
            self.fwriter_hi.writerow(data)


def main():
    root = tk.Tk()
    MainFrame(root)
    root.mainloop()


if __name__ == '__main__':
    main()
