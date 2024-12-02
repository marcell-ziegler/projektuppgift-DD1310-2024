from datetime import datetime
import pickle
import sys
import tkinter as tk
from tkinter import ttk

from biljettbokning.model import Carriage, Train


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.trains: list[Train] = [
            Train(
                159,
                datetime(2024, 12, 3, 15, 2),
                datetime(2024, 12, 3, 15, 30),
                "Stockholm C",
                "Uppsala C",
                carriages=[Carriage("2+2", 10)],
            ),
            Train(
                25,
                datetime(2024, 12, 3, 17, 2),
                datetime(2024, 12, 3, 18, 30),
                "Stockholm C",
                "Göteborg",
                carriages=[Carriage("2+2", 10)],
            ),
            Train(
                35,
                datetime(2024, 12, 3, 14, 2),
                datetime(2024, 12, 3, 15, 30),
                "Stockholm C",
                "Gävle",
                carriages=[Carriage("2+2", 10)],
            ),
            Train(
                2,
                datetime(2024, 12, 3, 12, 2),
                datetime(2024, 12, 3, 13, 30),
                "Umeå",
                "Uppsala C",
                carriages=[Carriage("2+2", 10)],
            ),
        ]
        self.trains.sort()

        self.menu_frame = MenuFrame(self)
        self.menu_frame.pack(expand=True, fill="both")

    def load(self, file_path: str) -> list[Train]:
        with open(file_path, "rb") as f:
            trains: list[Train] = pickle.load(f)
        return trains

    def book(self):
        pass

    def unbook(self):
        pass

    def print(self):
        pass

    def exit(self):
        self.destroy()
        sys.exit(0)


class MenuFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # Configure first row
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Add title
        self.title = ttk.Label(
            self,
            text="Tågbokning",
            justify="center",
            anchor="center",
            font=("TkTextFont", 24),
        )
        self.title.grid(column=0, row=0, sticky="nesw", pady=15)

        # Load all text representations of the trains in the app
        train_texts = [t.menu_text() for t in self.master.trains]  # type: ignore

        # Add configured rows for all trains
        for i in range(len(train_texts)):
            self.rowconfigure(i + 1, weight=3)

        # Make label widgets for all trains
        self.train_labels: list[ttk.Label] = []
        for i, train in enumerate(train_texts):
            self.train_labels.append(
                ttk.Label(
                    self, text=f"{i+1}.  {train}", justify="left", anchor="center"
                )
            )

        # load labels into app
        for i, label in enumerate(self.train_labels):
            label.grid(column=0, row=(i + 1), sticky="nsw", padx=(50, 0))

        # make the combobox
        options = [str(i + 1) for i in range(len(self.train_labels))]
        self.train_picker = ttk.Combobox(self, values=options)
        self.rowconfigure((len(self.train_labels) + 1), weight=1)
        self.train_picker.grid(column=0, row=(len(self.train_labels) + 1), pady=10)

        # Create frame for buttons
        self.button_frame = ttk.Frame(self)
        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.button_frame.columnconfigure(2, weight=1)
        self.button_frame.columnconfigure(3, weight=1)

        # Make buttons
        self.book_button = ttk.Button(
            self.button_frame, text="Boka", command=self.master.book  # type: ignore
        )
        self.book_button.grid(column=0, row=0, sticky="ns", padx=5, pady=5)
        self.book_button = ttk.Button(
            self.button_frame, text="Avboka", command=self.master.unbook  # type: ignore
        )
        self.book_button.grid(column=1, row=0, sticky="ns", padx=5, pady=5)
        self.book_button = ttk.Button(
            self.button_frame, text="Skriv ut biljetter", command=self.master.print  # type: ignore
        )
        self.book_button.grid(column=2, row=0, sticky="ns", padx=5, pady=5)
        self.book_button = ttk.Button(
            self.button_frame, text="Avsluta", command=self.master.exit  # type: ignore
        )
        self.book_button.grid(column=3, row=0, sticky="ns", padx=5, pady=5)

        # Add the button frame to the app
        self.button_frame.grid(column=0, row=(len(self.train_labels) + 2))


if __name__ == "__main__":
    app = App()
    app.mainloop()
