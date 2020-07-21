import tkinter as tk


class ConditionsFrame(tk.Toplevel):
    def __init__(self, root, num_of_conditions, conditions):
        self.root = root
        self.root.title("Conditions")
        self.conditions = conditions
        self.vals = []
        self.num_of_conditions = num_of_conditions

        self.fields = ['Condition', 'Delay', 'Perturbation',
                       'Cursor Perturbation Amplitude',
                       'Target Perturbation Amplitude',
                       'Visibility of Cursor',
                       'Visibility of Target']
        self.configure_table()

    def configure_table(self):
        for i in range(len(self.fields)):
            v1 = tk.StringVar()
            e1 = tk.Label(self.root, textvariable=v1)
            v1.set(self.fields[i])
            e1.grid(row=1, column=i+1)

        for i in range(self.num_of_conditions.get()):
            self.vals.append([])
            for j in range(len(self.fields)):
                if self.fields[j] == 'Condition':
                    ent = tk.Label(self.root, text=i+1)
                    ent.grid(row=i + 2, column=j + 1)
                else:
                    val = tk.IntVar()
                    ent = tk.Entry(self.root, textvariable=val)
                    ent.grid(row=i+2, column=j+1)
                    self.vals[i].append(val)

    def waiting(self):
        self.root.wait_window()

        conditions = []
        for i in range(self.num_of_conditions.get()):
            conditions.append({})
            for j in range(len(self.fields)):
                if self.fields[j] == 'Condition':
                    conditions[i][self.fields[j]] = i + 1
                else:
                    conditions[i][self.fields[j]] = self.vals[i][j - 1].get()

        return conditions
