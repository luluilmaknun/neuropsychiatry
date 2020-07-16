import tkinter as tk


class ConditionsFrame(tk.Toplevel):
    def __init__(self, root, num_of_condition):
        self.root = root
        self.frame = tk.Frame(self.root, width=360, height=360)
        self.root.title("Conditions")

        fields = ['Condition', 'Delay', 'Perturbation',
                  'Cursor Perturbation Amplitude',
                  'Target Perturbation Amplitude',
                  'Visibility of Cursor',
                  'Visibility of Target']
        self.configure_table(num_of_condition, fields)

    def configure_table(self, num, fields=[]):
        for i in range(len(fields)):
            v1 = tk.StringVar()
            e1 = tk.Entry(self.root, textvariable=v1, state='readonly')
            v1.set(fields[i])
            e1.grid(row=1, column=i+1)

        for i in range(num):
            for j in range(len(fields)):
                ent = tk.Entry(self.root)
                ent.grid(row=i+2, column=j+1)
