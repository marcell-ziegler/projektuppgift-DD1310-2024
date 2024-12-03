from datetime import datetime
import glob
import os
import random
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk

from biljettbokning.widgets.bookingpopup import BookingPopup
from biljettbokning.widgets.menuframe import MenuFrame
from biljettbokning.model import Booking, Bookings, Train
from biljettbokning.widgets.unbookingpopup import UnbookingPopup


class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.protocol("WM_DELETE_WINDOW", self.exit)

        self.withdraw()

        self.trains: list[Train] = []
        self.bookings = Bookings()

        self.popup = tk.Toplevel()
        self.popup.title("Ladda tåg?")
        popup_label = ttk.Label(
            self.popup, text="Vill du ladda tåg från befintliga filer eller slumpa nya?"
        )
        popup_label.grid(column=0, row=0, columnspan=2, padx=5, pady=15)

        load_button = ttk.Button(self.popup, text="Ladda in", command=self.load_trains)
        load_button.grid(column=0, row=1, padx=(10, 5), pady=5)

        rand_button = ttk.Button(
            self.popup, text="Slumpa nya", command=self.rand_trains
        )
        rand_button.grid(column=1, row=1, padx=(5, 10), pady=5)
        self.popup.grab_set()
        self.popup.focus()

        # Definition for type consistency
        self.menu_frame = MenuFrame(self)

    def finish_window(self):
        self.popup.grab_release()
        self.popup.destroy()
        self.deiconify()
        self.menu_frame = MenuFrame(self)
        self.menu_frame.pack(expand=True, fill="both")

    def load_trains(self):
        load_dir = filedialog.askdirectory(mustexist=True)
        train_paths = [
            os.path.join(load_dir, path)
            for path in glob.glob("./*", root_dir=load_dir)
            if os.path.isdir(os.path.join(load_dir, path))
        ]

        for train_path in train_paths:
            self.trains.append(Train.from_file(train_path))

        # Get amount of trains
        cur_trains_amount = len(self.trains)
        # Remove all departed
        self.trains = [
            train for train in self.trains if train.departure > datetime.now()
        ]

        # If departed trains exist
        if (cur_trains_amount - len(self.trains)) > 0:
            # Ta fram alla befintliga tågnummer
            cur_nums = [train.number for train in self.trains]
            # Ta fram alla möjliga
            nums = list(range(1000))
            # Remove existing
            for num in cur_nums:
                nums.remove(num)
            # Take enough nums
            new_nums = random.sample(nums, cur_trains_amount - len(self.trains))
            # Make new trains
            for num in new_nums:
                self.trains.append(Train.random(num))

        self.finish_window()

    def rand_trains(self):
        num_trains = random.randint(5, 17)
        train_nums = random.sample(list(range(1, 1000)), num_trains)
        for num in train_nums:
            self.trains.append(Train.random(num))

        self.finish_window()

    def book(self):
        """Make the booking popup."""
        try:
            train = self.menu_frame.get_train()
        except (ValueError, IndexError):
            # Visar felmedellande ifall inget tåg är valt
            messagebox.showerror(
                "Ogiltigt tåg!", "Inget tåg är valt i menyn, välj ett tåg!"
            )
        BookingPopup(train, self)

    def unbook(self):
        """Make the unbooking popup."""
        try:
            train = self.menu_frame.get_train()
        except (ValueError, IndexError):
            # Visar felmedellande ifall inget tåg är valt
            messagebox.showerror(
                "Ogiltigt tåg!", "Inget tåg är valt i menyn, välj ett tåg!"
            )
        UnbookingPopup(train, self)

    def print(self):
        window = tk.Toplevel()
        window.title("Skriv ut...")
        label = ttk.Label(
            window,
            text="Vilka bokningar skall skrivas ut?",
            anchor="center",
            justify="center",
        )
        label.grid(column=0, row=0, columnspan=3, pady=15, padx=5)

        all_button = ttk.Button(
            window, text="Allt", command=lambda: self.output_all_tickets(window)
        )
        all_button.grid(column=0, row=1, padx=(10, 5), pady=5)

        current_button = ttk.Button(
            window,
            text="Nuvarande",
            command=lambda: self.output_current_tickets(window),
        )
        current_button.grid(column=1, row=1, padx=5, pady=5)

        exit_button = ttk.Button(window, text="Tillbaka", command=window.destroy)
        exit_button.grid(column=2, row=1, padx=(5, 10), pady=5)

    def output_all_tickets(self, windows):
        dir_path = filedialog.askdirectory()
        # "The unholy indent" iterates over every seat in the current app state and prints them to files
        for train in self.trains:
            for car_num, car in enumerate(train.carriages):
                for seat in car._flat_seats:  # pylint: disable=W0212
                    if seat.is_booked():
                        with open(
                            os.path.join(
                                dir_path,
                                f"Tåg {train.number}"
                                " - "
                                f"{train.departure.isoformat(" ", "minutes").replace(":", "")}"
                                " - "
                                f"{seat.passenger_name}"
                                f" - {seat.number} {car_num+1}.txt",
                            ),
                            "w",
                            encoding="utf-8",
                        ) as f:
                            f.write(
                                str(
                                    Booking(
                                        (
                                            seat.passenger_name
                                            if seat.passenger_name
                                            else ""
                                        ),
                                        seat.number,
                                        car_num,
                                        train,
                                    )
                                )
                            )
        windows.destroy()

    def output_current_tickets(self, window):
        dir_path = filedialog.askdirectory(mustexist=True)

        for booking in self.bookings:
            with open(
                os.path.join(
                    dir_path,
                    f"Tåg {booking.train.number}"
                    " - "
                    f"{booking.train.departure.isoformat(" ", "minutes").replace(":", "")}"
                    " - "
                    f"{booking.name}"
                    f" - {booking.seat} {booking.carriage}.txt",
                ),
                "w",
                encoding="utf-8",
            ) as f:
                f.write(str(booking))

        window.destroy()

    def exit(self):

        save_trains = messagebox.askyesno("Spara tåg?", "Vill du spara tågen?")

        if save_trains:
            save_dir = filedialog.askdirectory()
            for train in self.trains:
                train.serialize(save_dir)

        self.destroy()
        sys.exit(0)


if __name__ == "__main__":
    app = App()
    app.mainloop()
