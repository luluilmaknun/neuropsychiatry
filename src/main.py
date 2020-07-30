"""
Test input
"""
import tkinter as tk
import numpy as np
import math
import nidaqmx
import src.constants as constants

# Window and nidaqmx task variable
is_zeroed = False  # button zero click if clicked, unknown functionality?
channel_zero_button_value = [0] * constants.CHANNEL_COUNT
channel_read_value = [0] * constants.CHANNEL_COUNT

# Cursor variable
cursor_position_data_buffer = [0] * constants.DELAY_BUFFER_LEN
cursor_position_data = 0
delay_pointer = 0   # what is this?
pertubation = 0

# Target variable
target_position_data = 0
is_target_moved = False

# Scoring variable
total_score = 0
current_score = 0
score_count = 0
norm_score = 0

# trial variable
trial_list = {
    'target_frequency': 0.4,
    'target_amplitude': 0.1,
    'cursor_frequency': 0,
    'cursor_amplitude': 0,
    'delay': 0,
}
phase_time = 0  # what is this?
current_phase = 0   # what is this?
next_phase_time = 0 # what is this?
number_of_output_data = 9
output_data = [0] * number_of_output_data

# Initialize window
master = tk.Tk()
master.minsize(width=constants.WINDOW_WIDTH, height=constants.WINDOW_LENGTH)
w = tk.Label(master)
w.pack()

# Initialize nidaqmx task
task = nidaqmx.task.Task("ReadVoltageTwoChannel")
task.ai_channels.add_ai_voltage_chan(
    "Dev1/ai0, Dev1/ai4",
    0,
    nidaqmx.constants.TerminalConfiguration.DIFFERENTIAL,
    constants.READ_DATA_MIN_VALUE,
    constants.READ_DATA_MAX_VALUE,
    nidaqmx.constants.VoltageUnits.VOLTS,
    0)
task.timing.cfg_samp_clk_timing(
    constants.READ_DATA_SAMPLE_RATE,
    0,
    nidaqmx.constants.Edge.RISING,
    nidaqmx.constants.AcquisitionType.CONTINUOUS,
    0)
ConstantOverwrite = nidaqmx.constants.OverwriteMode
task.in_stream.over_write = ConstantOverwrite.OVERWRITE_UNREAD_SAMPLES
task.start()

def init_new_phase():
    global current_phase, phase_time, next_phase_time, norm_score
    current_phase += 1
    if current_phase == constants.END_PHASE:
        current_phase = constants.START_PHASE
    phase_time = 0

    if current_phase == constants.START_PHASE:
        pass # init trial
    elif current_phase == constants.TRACK_PHASE:
        is_target_moved == True
        # make something (in)visible
        next_phase_time = constants.TRACK_TIME * constants.CLOCK_FREQUENCY
    elif current_phase == constants.SCORE_PHASE:
        # make something (in)visible
        norm_score = int(1000 * total_score / score_count)
        # display score
        next_phase_time = 200
        # toneoff ?
    elif current_phase == constants.REST_PHASE:
        #display '+' character
        next_phase_time = 100


def run():
    """
    function to read
    """
    data = task.read(constants.READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH)
    channel_read_value[0] = sum(data[0])/constants.READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH
    channel_read_value[1] = sum(data[1])/constants.READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH

    w['text'] = 'ai0: %.5f\nai4: %.5f' % (channel_read_value[0], channel_read_value[1])

    # One channel data processing
    cursor_position_data_buffer[delay_pointer] = (channel_read_value[0] - channel_zero_button_value[0]) * constants.CURSOR_SCALE - 1
    if not is_zeroed:
        channel_zero_button_value[0] = channel_read_value[0]
        zeroed = True

    cursor_position_data = cursor_position_data_buffer[((delay_pointer + constants.DELAY_BUFFER_LEN - trial_list["delay"] * constants.CLOCK_FREQUENCY) % constants.DELAY_BUFFER_LEN)]
    if abs(cursor_position_data) > 2000:
        cursor_position_data = np.sign(cursor_position_data) * 2000
    phase_time += 1
    if phase_time == next_phase_time:
        init_new_phase()
        
    if is_target_moved:
        sin_multiply_value = 2 * math.pi * phase_time * trial_list["target_frequency"] / constants.CLOCK_FREQUENCY
        target_position_data = trial_list["target_amplitude"] * math.sin(sin_multiply_value)

        sin_multiply_value = 2 * math.pi * phase_time * trial_list["cursor_frequency"] / constants.CLOCK_FREQUENCY
        pertubation = trial_list["cursor_amplitude"] * math.sin(sin_multiply_value)

        cursor_position_data += pertubation

        current_score = math.exp(-abs(cursor_position_data - target_position_data) / constants.SCORE_CONST)
        score_count += 1
        total_score += current_score
    else:
        current_score = 0
        target_position_data = 0

    #move target and cursor

    #data record
    output_data[0] = int(cursor_position_data * 500)
    output_data[1] = int(target_position_data * 500)
    output_data[2] = int(pertubation * 500)
    output_data[3] = current_phase
    output_data[4] = trial_list["condition"]
    output_data[5] = int(total_score)
    output_data[6] = score_count
    output_data[7] = int(current_score * 1000)
    output_data[8] = constants.READ_SAMPLE_PER_CHANNEL_PER_WINDOW_REFRESH

    delay_pointer = (delay_pointer + 1) % constants.DELAY_BUFFER_LEN
    master.after(constants.WINDOW_REFRESH_TIME, run)


run()
master.mainloop()
