import pickle
import tkinter as tk
from tkinter import ttk

from biljettbokning.model import Train


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")

        self.test_label = ttk.Label(self, text="Test")
        self.test_label.pack(fill="both", expand=True)
        self.trains: list[Train] = []

    def load(self, file_path: str) -> list[Train]:
        with open(file_path, "rb") as f:
            trains: list[Train] = pickle.load(f)
        return trains


if __name__ == "__main__":
    app = App()
    app.mainloop()
