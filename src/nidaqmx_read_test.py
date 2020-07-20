"""
Test input
"""
import tkinter as tk
import nidaqmx

master = tk.Tk()
master.minsize(width=400, height=400)
w = tk.Label(master)
w.pack()


def run():
    """
    function to read
    """
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(
            "Dev1/ai0",
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
        print('1 Channel 1 Sample Read: ')
        data = task.read()
        w['text'] = '%.2f' % data
    master.after(1000, run)


run()
master.mainloop()
