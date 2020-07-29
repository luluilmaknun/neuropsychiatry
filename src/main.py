"""
Test input
"""
import tkinter as tk
import nidaqmx
import constants

master = tk.Tk()
master.minsize(width=constants.WINDOW_WIDTH, height=constants.WINDOW_LENGTH)
w = tk.Label(master)
w.pack()
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


def run():
    """
    function to read
    """
    data = task.read(constants.READ_SAMPLE_PER_WINDOW_REFRESH)
    data_avg_chan1 = sum(data[0])/constants.READ_SAMPLE_PER_WINDOW_REFRESH
    data_avg_chan2 = sum(data[1])/constants.READ_SAMPLE_PER_WINDOW_REFRESH
    w['text'] = 'ai0: %.5f\nai4: %.5f' % (data_avg_chan1, data_avg_chan2)
    master.after(constants.WINDOW_REFRESH_TIME, run)


run()
master.mainloop()
