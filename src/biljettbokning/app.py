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
    """Container for controlling main GUI logic.

    Attributes:
        trains (list[Train]): list of all trains in the current run
        bookings (list[Booking]): list of all active bookings made in the current run
    """

    def __init__(self):
        super().__init__()

        # Bind the exit function to window close button.
        self.protocol("WM_DELETE_WINDOW", self.exit)

        # Minimise
        self.withdraw()

        self.trains: list[Train] = []
        self.bookings = Bookings()

        # Create popup to ask wether to load trains
        self.popup = tk.Toplevel()
        self.popup.title("Ladda tåg?")
        popup_label = ttk.Label(
            self.popup, text="Vill du ladda tåg från befintliga filer eller slumpa nya?"
        )
        popup_label.grid(column=0, row=0, columnspan=2, padx=5, pady=15)

        # Load existing trains button
        load_button = ttk.Button(self.popup, text="Ladda in", command=self.load_trains)
        load_button.grid(column=0, row=1, padx=(10, 5), pady=5)

        # Load new random trains
        rand_button = ttk.Button(
            self.popup, text="Slumpa nya", command=self.rand_trains
        )
        rand_button.grid(column=1, row=1, padx=(5, 10), pady=5)
        self.popup.grab_set()
        self.popup.focus()

        # Definition for type consistency
        self.menu_frame = MenuFrame(self)

    def finish_window(self):
        """Cleanup after trains have been loaded/randomised."""
        self.trains.sort()
        self.popup.grab_release()
        self.popup.destroy()
        self.deiconify()
        # Load the main menu
        self.menu_frame = MenuFrame(self)
        self.menu_frame.pack(expand=True, fill="both")

    def load_trains(self):
        """Ask where the trains are and load them into App."""
        load_dir = filedialog.askdirectory(mustexist=True)

        # Collect all directories in the specified place
        # Each is a train
        train_paths = [
            os.path.join(load_dir, path)
            for path in glob.glob("./*", root_dir=load_dir)
            if os.path.isdir(os.path.join(load_dir, path))
        ]

        # Load trains
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
            # Get all already used train numbers
            cur_nums = [train.number for train in self.trains]
            # Get all possible nums
            nums = list(range(1000))
            # Remove existing
            for num in cur_nums:
                nums.remove(num)
            # Take enough nums
            new_nums = random.sample(nums, cur_trains_amount - len(self.trains))
            # Make new trains
            for num in new_nums:
                self.trains.append(Train.random(num))

        # Cleanup
        self.finish_window()

    def rand_trains(self):
        """Populate the train list with random trains"""
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
            # Show error if there is no train chosen.
            messagebox.showerror(
                "Ogiltigt tåg!", "Inget tåg är valt i menyn, välj ett tåg!"
            )
            return
        # If sucess book
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
            return
        # if sucess, make popup
        UnbookingPopup(train, self)

    def print(self):
        """Handle ticket printing."""

        # Make a popup for asking to print all or some
        window = tk.Toplevel()
        window.title("Skriv ut...")
        label = ttk.Label(
            window,
            text="Vilka bokningar skall skrivas ut?",
            anchor="center",
            justify="center",
        )
        label.grid(column=0, row=0, columnspan=3, pady=15, padx=5)

        # All button bound to corresponding function
        all_button = ttk.Button(
            window, text="Allt", command=lambda: self.output_all_tickets(window)
        )
        all_button.grid(column=0, row=1, padx=(10, 5), pady=5)

        # Current tickets button with bindind to corrsponding funcion
        current_button = ttk.Button(
            window,
            text="Nuvarande",
            command=lambda: self.output_current_tickets(window),
        )
        current_button.grid(column=1, row=1, padx=5, pady=5)

        exit_button = ttk.Button(window, text="Tillbaka", command=window.destroy)
        exit_button.grid(column=2, row=1, padx=(5, 10), pady=5)

    def output_all_tickets(self, window):
        """Ask for destination and print all tickets to specified folder"""
        dir_path = filedialog.askdirectory()
        # "The unholy indent" iterates over every seat in the current app state and prints them to files
        # Givet that tehre are bookings in them
        for train in self.trains:
            for car_num, car in enumerate(train.carriages):
                for seat in car._flat_seats:  # pylint: disable=W0212
                    if seat.is_booked():
                        with open(
                            # Make filepath as Tåg NN - YYYY-MM-DD HH.MM - Name Namesson - seat car.txt
                            # Last part is for guaranteed uniqueness
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
                                            else ""  # Only for type securty, never happens (is_booked == True) # noqa
                                        ),
                                        seat.number,
                                        car_num,
                                        train,
                                    )
                                )
                            )

        # Remove popup
        window.destroy()

    def output_current_tickets(self, window):
        """Ask user for destination and output only the tickets that are stored in the apps current run."""
        dir_path = filedialog.askdirectory(mustexist=True)

        # Iterate over bookings and print
        for booking in self.bookings:
            with open(
                # Make filepath as Tåg NN - YYYY-MM-DD HH.MM - Name Namesson - seat car.txt
                # Last part is for guaranteed uniqueness
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

        # Destroy popup
        window.destroy()

    def exit(self):
        """Ask wether to save trains and close the program."""
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
