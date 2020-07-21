"""
Test input
"""
import tkinter as tk
import nidaqmx

master = tk.Tk()
master.minsize(width=400, height=400)
w = tk.Label(master)
w.pack()
task = nidaqmx.task.Task()
task.ai_channels.add_ai_voltage_chan(
    "Dev1/ai0, Dev1/ai4",
    0,
    nidaqmx.constants.TerminalConfiguration.DIFFERENTIAL,
    -10, 10,
    nidaqmx.constants.VoltageUnits.VOLTS,
    0)
task.timing.cfg_samp_clk_timing(
    5000,
    0,
    nidaqmx.constants.Edge.RISING,
    nidaqmx.constants.AcquisitionType.CONTINUOUS,
    0)
constant_overwrite = nidaqmx.constants.OverwriteMode
task.in_stream.over_write = constant_overwrite.OVERWRITE_UNREAD_SAMPLES
task.start()


def run():
    """
    function to read
    """
    global task
    data = task.read(100)
    data_avg_chan1 = sum(data[0])/100
    data_avg_chan2 = sum(data[1])/100
    w['text'] = '%.5f, %.5f' % (data_avg_chan1, data_avg_chan2)
    master.after(10, run)

run()
master.mainloop()
