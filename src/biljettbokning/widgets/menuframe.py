from collections import defaultdict
from datetime import date
from tkinter import ttk
import tkinter as tk
from biljettbokning.model import Train


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

        trains_by_date: dict[date, list[str]] = defaultdict(list)
        for train in self.master.trains:  # type: ignore
            train: Train
            trains_by_date[train.departure.date()].append(train.menu_text())

        # Make label widgets for all trains
        self.train_labels: list[ttk.Label] = []
        i = 1
        train_index = 1
        for cur_date in sorted(list(trains_by_date.keys())):
            # Append a date label
            label = ttk.Label(
                self, text=cur_date.isoformat(), anchor="center", justify="center"
            )
            self.rowconfigure(i, weight=2)
            label.grid(column=0, row=i, sticky="nsew", padx=5, pady=(15, 5))
            self.train_labels.append(label)
            i += 1
            for train_str in trains_by_date[cur_date]:
                label = ttk.Label(
                    self,
                    text=f"{train_index}. " + train_str,
                    anchor="center",
                    justify="center",
                )
                self.rowconfigure(i, weight=1)
                label.grid(column=0, row=i, sticky="nsew", padx=5, pady=2)
                self.train_labels.append(label)

                i += 1
                train_index += 1

        # Make frame for Combobox
        self.select_frame = ttk.Frame(self)
        self.select_frame.rowconfigure(0, weight=1)
        self.select_frame.columnconfigure(0, weight=1)
        self.select_frame.columnconfigure(1, weight=1)

        self.select_frame_label = ttk.Label(
            self.select_frame, text="Välj ett tåg ur listan:", justify="right"
        )
        self.select_frame_label.grid(column=0, row=0, sticky="e")

        # Make the combobox
        options = list([str(i) for i in range(1, train_index)])
        self.selected_train = tk.StringVar()
        self.train_picker = ttk.Combobox(
            self.select_frame, values=options, textvariable=self.selected_train
        )
        self.rowconfigure((len(self.train_labels) + 1), weight=1)
        self.train_picker.grid(column=1, row=0, sticky="w")

        # Add box and label
        self.select_frame.grid(
            column=0, row=(len(self.train_labels) + 1), sticky="nesw", pady=10
        )

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

    def get_train(self) -> Train:
        return self.master.trains[int(self.selected_train.get()) - 1]  # type: ignore
