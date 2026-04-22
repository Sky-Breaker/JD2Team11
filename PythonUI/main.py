import tkinter as tk
from tkinter import ttk

def initialize_GUI():
    root = tk.Tk()
    frame = ttk.Frame(root, padding=10)
    frame.grid()

    ttk.Label(frame, text="Hello, world!").grid(column=0, row=0)
    ttk.Button(frame, text="Wow").grid(column=0, row=1)

    root.mainloop()


if __name__ == "__main__":
    initialize_GUI()