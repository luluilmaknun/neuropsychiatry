import tkinter as tk
from src.ui.settings import SettingsFrame


class MainFrame(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, *kwargs)
        self.pack()
        self.root = root
        self.root.title("Neuropsikiatri")

        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        self.root.geometry("%dx%d+0+0" % (w, h))

        # BUTTON "Change Settings"
        self.btn_settings = tk.Button(self, text="Change Settings",
                                      command=self.open_settings)
        self.btn_settings.pack(anchor=tk.NW)

    def open_settings(self):
        self.settings_frame = tk.Toplevel(self.root)
        self.app = SettingsFrame(self.settings_frame)


def main():
    root = tk.Tk()
    MainFrame(root)
    root.mainloop()


if __name__ == '__main__':
    main()
