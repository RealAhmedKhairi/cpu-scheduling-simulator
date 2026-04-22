import tkinter as tk

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CPU Scheduling Simulator")
        self.root.geometry("900x600")

    def run(self):
        self.root.mainloop()