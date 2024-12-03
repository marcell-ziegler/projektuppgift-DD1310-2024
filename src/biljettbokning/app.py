from datetime import datetime
import pickle
import sys
import tkinter as tk
from tkinter import messagebox

from biljettbokning.widgets.bookingpopup import BookingPopup
from biljettbokning.widgets.menuframe import MenuFrame
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
                carriages=[Carriage("3+2", 10), Carriage("3+2", 15)],
            ),
            Train(
                35,
                datetime(2024, 12, 3, 14, 2),
                datetime(2024, 12, 3, 15, 30),
                "Stockholm C",
                "Gävle",
                carriages=[Carriage("2+2", 4)],
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

        self.trains[0].book_passenger(0, 15, "John Doe")

        self.menu_frame = MenuFrame(self)
        self.menu_frame.pack(expand=True, fill="both")

    def load(self, file_path: str) -> list[Train]:
        with open(file_path, "rb") as f:
            trains: list[Train] = pickle.load(f)
        return trains

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
        pass

    def print(self):
        pass

    def exit(self):
        self.destroy()
        sys.exit(0)


if __name__ == "__main__":
    app = App()
    app.mainloop()
