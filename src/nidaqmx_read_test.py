from tkinter import *
import nidaqmx

master = Tk()
master.minsize(width=400, height=400)
w = Label(master) #shows as text in the window
w.pack() #organizes widgets in blocks before placing them in the parent.   

def run():
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("Dev1/ai0", 0, nidaqmx.constants.TerminalConfiguration.DIFFERENTIAL, -10, 10, nidaqmx.constants.VoltageUnits.VOLTS, 0)
        task.timing.cfg_samp_clk_timing(5000, 0, nidaqmx.constants.Edge.RISING, nidaqmx.constants.AcquisitionType.CONTINUOUS, 0)
        task.in_stream.over_write=nidaqmx.constants.OverwriteMode.OVERWRITE_UNREAD_SAMPLES
        print('1 Channel 1 Sample Read: ')
        data = task.read()
        w['text'] = '%.2f' % data #said sensor value
    master.after(1000, run)

run() # run the function once.
master.mainloop()