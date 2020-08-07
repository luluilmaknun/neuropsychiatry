import tkinter as tk
import tkinter.filedialog as tk_fd
import os
import nidaqmx
import numpy as np
import math
import win32file
import win32event
import src.constants as constants

from src.ui.settings import SettingsFrame
from src.ui.playground import Playground


class MainFrame(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, *kwargs)
        self.pack(anchor=tk.CENTER, fill=tk.Y)
        self.root = root
        self.root.title("Neuropsikiatri")

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
        self.perturbation = 0

        # Init scoring variable
        self.total_score = 0
        self.current_score = 0
        self.score_count = 0
        self.norm_score = 0

        # Init trial variable
        self.phase_time = 0
        self.current_phase = 0
        self.next_phase_time = 0
        self.list_counter = 0
        self.is_task_on = False

        # Init record data variable
        self.data = [[]] * constants.CHANNEL_COUNT
        self.output_data = [0] * constants.NUM_LO
        self.buf_hi = [0] * constants.LEN_BUF_HI
        self.buf_lo = [0] * constants.LEN_BUF_HI
        self.curhalf_hi, self.curhalf_lo = 0, 0
        self.fileoffset_hi, self.fileoffset_lo, self.pointer_lo, self.pointer_hi = 0, 0, 0, 0
        self.ov_hi, self.ov_lo = win32file.OVERLAPPED(), win32file.OVERLAPPED()

        # Set MainFrame width and height based on screen size
        self.w = self.root.winfo_screenwidth()
        self.h = self.root.winfo_screenheight()
        self.root.geometry("%dx%d+0+0" % (self.w, self.h))

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

    def init_new_phase(self):
        self.current_phase += 1
        if self.current_phase == constants.END_PHASE:
            self.current_phase = constants.START_PHASE
        self.phase_time = 0

        if self.current_phase == constants.START_PHASE:
            self.next_phase_time = 100 #temp
            # init trial
        elif self.current_phase == constants.TRACK_PHASE:
            self.is_target_moved = True
            # make something (in)visible
            self.next_phase_time = constants.TRACK_TIME * constants.CLOCK_FREQUENCY
        elif self.current_phase == constants.SCORE_PHASE:
            # make something (in)visible
            self.norm_score = int(1000 * self.total_score / self.score_count)
            # display score
            self.next_phase_time = 200
            # toneoff ?
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
        self.record_icon = self.record_canvas.create_oval(0, 0, 60, 60,
                                                          fill="red3", outline="")

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
        self.record_on = tk.BooleanVar()
        tk.Checkbutton(self.button_frame, text="Record", var=self.record_on, font=("Arial", 16),
                       onvalue=True, offvalue=False).pack()

        # FILE MANAGER
        self.file_frame = tk.Frame(self.right_frame)
        self.file_frame.grid(columnspan=2, sticky=tk.E)
        self.record_dir = tk.StringVar()
        self.record_dir.set(os.path.expanduser("~"))
        self.record_dir_entry = tk.Entry(self.file_frame, font=("Arial", 12), width=25,
                                         textvariable=self.record_dir)
        self.record_dir_entry.pack()
        self.record_dir_entry.bind("<1>", self.change_dir)

        self.record_name = tk.StringVar(value='test')
        self.record_name_entry = tk.Entry(self.file_frame, font=("Arial", 12), width=18,
                                              textvariable=self.record_name)
        self.record_name_entry.pack(side='left', padx=2)

        self.record_number = tk.IntVar(value=1)
        self.record_number_entry = tk.Entry(self.file_frame, font=("Arial", 12), width=6,
                                                textvariable=self.record_number)
        self.record_number_entry.pack(side='left', padx=1)

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

    def run(self):
        self.data = self.nidaq_task.read(constants.READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH)
        self.channel_read_value[0] = sum(self.data[0])/constants.READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH
        self.channel_read_value[1] = sum(self.data[1])/constants.READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH

        # One channel data processing
        self.cursor_position_data_buffer[self.delay_pointer] = (self.channel_read_value[0] - self.channel_zero_button_value[0]) * constants.CURSOR_SCALE - 1
        if not self.is_zeroed:
            self.channel_zero_button_value[0] = self.channel_read_value[0]
            self.is_zeroed = True

        self.cursor_position_data = self.cursor_position_data_buffer[((self.delay_pointer + constants.DELAY_BUFFER_LEN - 1 * constants.CLOCK_FREQUENCY) % constants.DELAY_BUFFER_LEN)] # still need to round
        if abs(self.cursor_position_data) > 2000:
            self.cursor_position_data = np.sign(self.cursor_position_data) * 2000
        self.phase_time += 1

        if self.phase_time == self.next_phase_time:
            self.init_new_phase()

        if self.is_target_moved:
            self.target_position_data = self.playground.move_target(1, 0.4, self.phase_time)
            
            self.cursor_position_data, self.perturbation = self.playground.move_cursor(self.cursor_position_data,
                                                                                      1, 0.4, self.phase_time)

            self.current_score = math.exp(-abs(self.cursor_position_data - self.target_position_data) / constants.SCORE_CONST)
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
        self.playground.move_cursor(self.cursor_position_data, 0, 0, self.phase_time)

        waserror = False
        if self.record_on.get():
            record_dir = self.record_dir.get()
            record_name = self.record_name.get()
            record_number = self.record_number.get()

            if not os.path.isdir(record_dir):
                os.makedirs(record_dir)
            root = record_dir + "\\" + record_name
            waserror = False

            self.ov_hi.hEvent = win32event.CreateEvent(None, 0, 0, None)
            self.ov_lo.hEvent = win32event.CreateEvent(None, 0, 0, None)

            # TODO: Error handling
            fn_hi = root + "hi-" + str(record_number) + '.sp'
            self.fid_hi = win32file.CreateFile(fn_hi,
                                               win32file.GENERIC_WRITE,
                                               0,
                                               None,
                                               win32file.CREATE_ALWAYS,
                                               win32file.FILE_FLAG_OVERLAPPED,
                                               None)
            self.fileoffset_hi = 0

            fn_lo = root + "lo-" + str(record_number) + '.sp'
            self.fid_lo = win32file.CreateFile(fn_lo,
                                               win32file.GENERIC_WRITE,
                                               0,
                                               None,
                                               win32file.CREATE_ALWAYS,
                                               win32file.FILE_FLAG_OVERLAPPED,
                                               None)
            self.fileoffset_lo = 0

            self.curhalf_hi = 0
            self.curhalf_lo = 0

            self.pointer_hi = 0
            self.pointer_lo = 0

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
            self.is_task_on = True
            self.run()

    def stop(self):
        self.start_stop_button['text'] = "Start"
        self.start_stop_button['command'] = self.start
        self.record_dir_entry['state'] = 'normal'
        self.record_name_entry['state'] = 'normal'
        self.record_number_entry['state'] = 'normal'
        self.nidaq_task.stop()

        if self.record_on.get():
            # SAVE FILE
            self.ov_hi.Offset = self.fileoffset_hi
            self.ov_hi.OffsetHigh = 0
            id_hi = (self.curhalf_hi * constants.LEN_BUF_HI) // 2
            num_bytes_hi = (self.pointer_hi % (constants.LEN_BUF_HI // 2)) * 2
            data_hi = self.buf_hi[id_hi].to_bytes(num_bytes_hi, 'little', signed=True)
            er = win32file.WriteFile(self.fid_hi,
                                     data_hi,
                                     self.ov_hi)

            self.ov_lo.Offset = self.fileoffset_lo
            self.ov_lo.OffsetHigh = 0
            id_lo = (self.curhalf_lo * constants.LEN_BUF_LO) // 2
            num_bytes_lo = (self.pointer_lo % (constants.LEN_BUF_LO // 2)) * 2
            data_lo = self.buf_lo[id_lo].to_bytes(num_bytes_lo, 'little', signed=True)
            er = win32file.WriteFile(self.fid_lo,
                                     data_lo,
                                     self.ov_lo)

            win32file.CloseHandle(self.fid_hi)
            win32file.CloseHandle(self.fid_lo)

            # Change record icon and increase record number
            current_id = self.record_number_entry.get()
            self.record_number.set(str(current_id) + 1)
            self.record_canvas.itemconfig(self.record_icon, fill='red3')

        # Init nidaqmx task variable
        self.is_zeroed = False  # button zero if clicked, unknown functionality?
        self.channel_zero_button_value = [0] * constants.CHANNEL_COUNT
        self.channel_read_value = [0] * constants.CHANNEL_COUNT

        # Init target variable
        self.target_position_data = 0
        self.is_target_moved = False
        self.is_task_on = False

        # Init cursor variable
        self.cursor_position_data_buffer = [0] * constants.DELAY_BUFFER_LEN
        self.cursor_position_data = 0
        self.delay_pointer = 0   # what is this?
        self.perturbation = 0

        # Init scoring variable
        self.total_score = 0
        self.current_score = 0
        self.score_count = 0
        self.norm_score = 0

        # Init trial variable
        self.phase_time = 0
        self.current_phase = 0
        self.next_phase_time = 0

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
            for i in range(constants.NUM_LO):
                self.buf_lo[self.pointer_lo + i] = self.output_data[i]
            self.pointer_lo = (self.pointer_lo + constants.NUM_LO) % constants.LEN_BUF_LO

            thishalf = self.pointer_lo // (constants.LEN_BUF_LO // 2)
            if thishalf != self.curhalf_lo:
                self.ov_lo.Offset = self.fileoffset_lo
                self.ov_lo.OffsetHigh = 0
                self.fileoffset_lo = self.fileoffset_lo + constants.LEN_BUF_LO
                id_lo = (self.curhalf_lo * constants.LEN_BUF_LO) // 2
                data_lo = self.buf_lo[id_lo].to_bytes(constants.LEN_BUF_LO, 'little', signed=True)
                er1 = win32file.WriteFile(self.fid_lo,
                                         data_lo,
                                         self.ov_lo)
                self.curhalf_lo = 1 - self.curhalf_lo

            for i in range(constants.READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH):
                for j in range(constants.CHANNEL_COUNT):
                    self.buf_hi[self.pointer_hi + j] = int(1000 * self.data[j][i])
                self.pointer_hi = (self.pointer_hi + constants.CHANNEL_COUNT) % constants.LEN_BUF_HI

            thishalf = self.pointer_hi // (constants.LEN_BUF_HI // 2)
            if thishalf != self.curhalf_hi:
                self.ov_hi.Offset = self.fileoffset_hi
                self.ov_hi.OffsetHigh = 0
                self.fileoffset_hi = self.fileoffset_hi + constants.LEN_BUF_HI
                id_hi = (self.curhalf_hi * constants.LEN_BUF_HI) // 2
                data_hi = self.buf_hi[id_hi].to_bytes(constants.LEN_BUF_HI, 'little', signed=True)
                er2 = win32file.WriteFile(self.fid_hi,
                                         data_hi,
                                         self.ov_hi)
                self.curhalf_hi = 1 - self.curhalf_hi


def main():
    root = tk.Tk()
    MainFrame(root)
    root.mainloop()


if __name__ == '__main__':
    main()
