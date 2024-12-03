import tkinter as tk
from tkinter import ttk, messagebox, font

from biljettbokning.model import Booking, Bookings, Train


class UnbookingPopup(tk.Toplevel):
    def __init__(self, train: Train, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.train = train

        # Make rows and columns
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)

        # Make the title
        self.title = ttk.Label(
            self,
            text=f"Avboka från tåg {train.number}",
            font=("TkTextFont", 24),
            anchor="center",
            justify="center",
        )
        self.title.grid(column=0, row=0, columnspan=2, sticky="nesw", pady=15)

        # Create the train visualisation
        mono_font = font.nametofont("TkFixedFont")
        mono_font.config(size=10)
        self.vis_label_var = tk.StringVar(value=train.terminal_repr())
        self.vis_label = ttk.Label(
            self,
            textvariable=self.vis_label_var,
            anchor="center",
            font=mono_font,
        )
        self.vis_label.grid(column=0, row=1, columnspan=2, sticky="ew", pady=10)

        self.selection_frame = SelectionFrame(self)
        self.selection_frame.grid(column=0, row=2, sticky="nesw")

    def unbook_passenger(self, car_num: str, selection_type: str, to_be_unbooked: str):
        try:
            carriage_num = int(car_num) - 1
            assert 0 <= carriage_num < len(self.train.carriages)
        except (ValueError, AssertionError):
            messagebox.showerror(
                "Ogiltigt vagnsnummer!",
                "Vagnsnumret du har angivit är antignen för stort/litet eller inte ett heltal",
            )
            self.focus()
            return

        if selection_type == "num":
            self.unbook_num(carriage_num, to_be_unbooked)
        else:
            self.unbook_name(carriage_num, to_be_unbooked)

    def unbook_num(self, carriage_num: int, seat_num_str: str):
        try:
            seat_num = int(seat_num_str)
            assert 0 <= seat_num < self.train.carriages[carriage_num].total_seats
        except (ValueError, AssertionError):
            messagebox.showerror(
                "Ogiltigt stolsnummer!",
                "Stolsnumret du har angivit är oitligt. Antingen för stort/litet eller inte ett heltal.",
            )
            self.focus()
            return

        # Try to remove booking from app state
        try:
            self.master.bookings.remove(self.train.number, carriage_num + 1, seat_num)  # type: ignore
        except ValueError:
            # This means no booking exists, can pass silently
            pass
        except Bookings.MultipleError:
            messagebox.showerror(
                "Kan inte ta bort bokning!",
                "Fler än en finns av samma bokning!",
            )
            self.focus()
            return

        # Cant raise error since it works with empty seats
        self.train.unbook_seat(carriage_num, seat_num)
        self.unbooking_complete()

    def unbook_name(self, carriage_num: int, name: str):
        # Try to unbook and brach for different errors
        try:
            seat = self.train.carriages[carriage_num].get_seat_name(name)
        except ValueError:
            messagebox.showerror(
                "Flera med samma namn!",
                "Det finns mer än en stol med detta namn, använd stolsnummer i stället.",
            )
            self.focus()
            return
        except KeyError:
            messagebox.showerror(
                "Ingen med detta namn!",
                "Det finns ingen stol i denna vagna med detta namn. Försök igen.",
            )
            self.focus()
            return

        try:
            self.master.bookings.remove(self.train.number, carriage_num + 1, seat.number)  # type: ignore
        except ValueError:
            # This means no booking exists, can pass silently
            pass
        except Bookings.MultipleError:
            messagebox.showerror(
                "Kan inte ta bort bokning!",
                "Fler än en finns av samma bokning!",
            )
            self.focus()
            return

        self.train.unbook_seat(carriage_num, seat.number)
        self.unbooking_complete()

    def unbooking_complete(self, nopopup=False):
        if not nopopup:
            messagebox.showinfo("Slutfört", "Avbokning slutförd!")
        # Update train visualisation
        self.vis_label_var.set(self.train.terminal_repr())
        # Clear inputs
        self.selection_frame.car_num.set("")
        self.selection_frame.multi_entry_var.set("")
        self.focus()


class SelectionFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=3)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        # Car number input
        self.car_num_label = ttk.Label(self, text="Vagnnummer:")
        self.car_num_label.grid(column=0, row=0, sticky="e", padx=5)
        self.car_num = tk.StringVar()
        self.car_num_entry = ttk.Entry(self, textvariable=self.car_num)
        self.car_num_entry.grid(column=1, row=0, sticky="w", pady=5, padx=5)

        # Multi-input for seat num/pax name
        self.multi_label_var = tk.StringVar(value="Stolsnummer:")
        self.multi_label = ttk.Label(self, textvariable=self.multi_label_var)
        self.multi_label.grid(column=0, row=1, sticky="e", padx=5, rowspan=2)
        self.multi_entry_var = tk.StringVar()
        self.multi_entry = ttk.Entry(self, textvariable=self.multi_entry_var)
        self.multi_entry.grid(column=1, row=1, sticky="w", pady=5, padx=5, rowspan=2)

        # Radio buttons for picking name or number
        self.selection_type = tk.StringVar(value="num")
        # Add trace to update text field when type changes
        self.selection_type.trace_add("write", self.on_change_type_selection)
        self.radio_label = ttk.Label(self, text="Välj baserat på:")
        self.radio_label.grid(column=2, row=0, sticky="w", padx=5)
        self.num_button = ttk.Radiobutton(
            self, variable=self.selection_type, value="num", text="Stolsnummer"
        )
        self.num_button.grid(column=2, row=1, sticky="w", padx=5, pady=5)
        self.name_button = ttk.Radiobutton(
            self, variable=self.selection_type, value="name", text="Namn"
        )
        self.name_button.grid(column=2, row=2, sticky="w", padx=5, pady=5)

        # Add buttons
        self.button_frame = ttk.Frame(self)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.button_frame.rowconfigure(0, weight=1)
        self.unbook_button = ttk.Button(
            self.button_frame,
            text="Avboka",
            command=lambda: self.master.unbook_passenger(  # type: ignore
                self.car_num.get(),
                self.selection_type.get(),
                self.multi_entry_var.get(),
            ),
        )
        self.unbook_button.grid(column=0, row=0)
        self.finish_button = ttk.Button(
            self.button_frame, text="Tillbaka", command=self.master.destroy
        )
        self.finish_button.grid(column=1, row=0)
        self.button_frame.grid(
            column=0, row=3, columnspan=3, padx=5, pady=5, sticky="nesw"
        )

    def on_change_type_selection(self, *_):
        if self.selection_type.get() == "num":
            self.multi_label_var.set("Stolsnummer:")
        else:
            self.multi_label_var.set("Namn:")

        self.multi_entry_var.set("")
