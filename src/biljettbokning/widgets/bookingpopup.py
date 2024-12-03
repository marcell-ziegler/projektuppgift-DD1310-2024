from copy import deepcopy
import tkinter as tk
from tkinter import ttk, messagebox, font
from biljettbokning.model import Booking, Train


class BookingPopup(tk.Toplevel):
    def __init__(self, train: Train, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.train = train

        # Make rows and columns
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)

        # Make the title
        self.title = ttk.Label(
            self,
            text=f"Boka tåg {train.number}",
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
        self.vis_label.grid(column=0, row=1, columnspan=2, sticky="ew")

        self.starting_seat = tk.StringVar()
        self.carriage_num = tk.StringVar()

        # Frame for picking seat
        self.select_frame = SelectFrame(self)
        self.select_frame.grid(column=0, row=2, sticky="nesw", pady=10, padx=5)

        # Frame for adding passengers
        self.pax_frame = PassengerFrame(self)
        self.pax_frame.grid(column=1, row=2, sticky="nesw", pady=5, padx=5)
        self.pax_frame.listbox.bind("<Configure>", self.on_listbox_configure)

    def book_passengers(self):
        """Book the passengers currently in the listbox starting at the seat given.

        Raises:
            nothing, all errors are handled with messageboxes

        """
        # region ErrorCheck
        # Testa läs vagnnr
        try:
            carriage_num = int(self.carriage_num.get()) - 1
            assert 0 <= carriage_num < len(self.train.carriages)
        except (ValueError, AssertionError):
            messagebox.showerror(
                "Ogiltigt vagnsnummer",
                "Vagnsnumret är ogiltigt! (Antingen ingen int, eller för stor/liten)",
            )
            self.focus()
            return

        # Testa läs startstol
        try:
            start_seat = int(self.starting_seat.get())
            assert 0 < start_seat <= self.train.carriages[carriage_num].total_seats
        except (ValueError, AssertionError):
            messagebox.showerror(
                "Ogiltigt stolsnummer!", "Stolsnumret du har angivit är ogiltigt!"
            )
            self.focus()
            return

        if (
            self.train.carriages[carriage_num].remaining_seats
            < self.pax_frame.listbox.size()
        ):
            messagebox.showerror(
                "Inte nog med stolar!",
                "Det finns inte tillräckligt med stolar i denna vagn för att genomföra bokningen.",
            )
            self.focus()
            return
        # endregion

        # With only one passenger, no checks for adjacent seats are neccesary
        if self.pax_frame.listbox.size() == 1:
            try:
                self.train.book_passenger(
                    carriage_num, start_seat, self.pax_frame.listbox.get(0)
                )
                self.master.bookings.append(  # type: ignore
                    Booking(
                        self.pax_frame.listbox.get(0),
                        start_seat,
                        carriage_num + 1,
                        deepcopy(self.train),
                    )
                )
            except ValueError:
                messagebox.showerror(
                    "Redan bokad plats!", "Den platsen är redan bokad av någon annan!"
                )
                self.focus()

            self.booking_complete()
            return

        # Remaining passengers if adjacency fails
        remaining: list[str] = []

        # If there are multiple they are iterated over until either:
        # All are booked, or
        # Adjacent places are not available
        for i, name in enumerate(self.pax_frame.listbox.get(0, tk.END)):

            # Flag for booking separate seats, givet user agreement
            book_separate = False
            try:
                self.train.book_passenger(carriage_num, start_seat + i, name)
                self.master.bookings.append(  # type: ignore
                    Booking(
                        name, start_seat + i, carriage_num + 1, deepcopy(self.train)
                    )
                )
            except (ValueError, IndexError):
                book_separate = messagebox.askokcancel(
                    "Inga intilliggande platser tillgängliga!",
                    "Det är inte möjligt att boka alla passagerare intill varandra. Vill du boka skiljda platser?",  # noqa
                )
                # Get the remaining passengers (current to end)
                remaining = self.pax_frame.listbox.get(i, tk.END)
                # Store last seat checked
                last_seat = start_seat + i
                self.focus()
                break
        else:
            # Assuming sucessful iteration, return
            self.booking_complete()
            return

        # return if user declines separate seats
        if not book_separate:
            messagebox.showinfo(
                "Börja om.",
                "Välj en ny plats att starta från där intilligande platser finns tillgängliga.",
            )
            self.focus()
            self.booking_complete(True)
            return

        # Concatenate remaining seats in car,
        # as well as the seats from 1 to current seat
        # In reverse order for intuitive and efficient pop
        seats_to_check: list[int] = list(
            reversed(
                list(
                    range(
                        last_seat + 1,
                        self.train.carriages[carriage_num].total_seats,
                    )
                )
                + list(
                    range(last_seat - 1, 0, -1)  # Reversed to be as close as possible
                )
            )
        )

        # Iterate over remaining passengers
        for name in remaining:
            is_booked = False
            while not is_booked:
                # Try next available seat
                # If it fails (no seats left in car)
                # break, show error and return
                try:
                    current_seat = seats_to_check.pop()
                except IndexError:
                    break

                # Try to book the passenger. If fail, try next seat in seats_to_check
                try:
                    self.train.book_passenger(carriage_num, current_seat, name)
                    self.master.bookings.append(  # type: ignore
                        Booking(
                            name, current_seat, carriage_num + 1, deepcopy(self.train)
                        )
                    )
                    # Set flag to stop iteration
                    is_booked = True
                except (ValueError, IndexError):
                    continue
            else:
                continue

            # Error and return for failed loop
            messagebox.showerror(
                "Bokning inte möjlig!",
                "Det gick inte att boka er i samma vagn, försök med en annan vagn.",
            )
            break
        else:
            self.focus()
            self.booking_complete()
            return

    def booking_complete(self, nopopup=False):
        if not nopopup:
            messagebox.showinfo("Slutfört", "Bokning slutförd!")
        # Update train visualisation
        self.vis_label_var.set(self.train.terminal_repr())
        # Clear inputs
        self.carriage_num.set("")
        self.starting_seat.set("")
        self.pax_frame.passenger_to_be_added.set("")
        # Clear passengers
        self.pax_frame.listbox.delete(0, tk.END)
        self.focus()

    def on_listbox_configure(self, _):
        """Adjust height of the listbox to current number of items."""
        self.pax_frame.listbox.config(height=self.pax_frame.listbox.size())


class PassengerFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)

        # Container for all names
        self.listbox = tk.Listbox(self, height=1)
        self.listbox.grid(column=0, row=0, columnspan=2, sticky="nesw", padx=5, pady=5)

        # add passenger-addition entry
        self.passenger_to_be_added = tk.StringVar()
        self.add_entry = ttk.Entry(self, textvariable=self.passenger_to_be_added)
        self.add_entry.grid(column=0, row=1, sticky="e", padx=5, pady=2)

        # add passenger-addition button
        self.add_button = ttk.Button(
            self, text="Lägg till passagerare", command=self.add_passenger
        )
        self.add_button.grid(column=1, row=1, sticky="w", padx=5, pady=2)

        # remove selected button
        self.remove_button = ttk.Button(
            self, text="Ta bort vald passagerare", command=self.remove_passenger
        )
        self.remove_button.grid(
            column=0, row=2, columnspan=2, sticky="ew", padx=5, pady=2
        )

    def add_passenger(self):
        passenger_name = self.passenger_to_be_added.get()
        if passenger_name:
            self.listbox.insert(tk.END, passenger_name)
            self.listbox.event_generate("<Configure>")

    def remove_passenger(self):
        index = self.listbox.curselection()[0]
        self.listbox.delete(index)
        self.listbox.event_generate("<Configure>")


class SelectFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Starting seat number picker
        self.starting_seat_label = ttk.Label(
            self,
            text="Välj stolsnummer (att börja ifrån):",
            justify="right",
        )
        self.starting_seat_label.grid(column=0, row=0, sticky="e")

        self.starting_seat_entry = ttk.Entry(
            self, textvariable=self.master.starting_seat  # type: ignore
        )
        self.starting_seat_entry.grid(column=1, row=0, sticky="w")

        # Carriage number
        self.carriage_num_label = ttk.Label(self, text="Vagnsnummer:", justify="right")
        self.carriage_num_label.grid(column=0, row=1, sticky="e")

        self.carriage_entry = ttk.Entry(self, textvariable=self.master.carriage_num)  # type: ignore
        self.carriage_entry.grid(column=1, row=1, sticky="w")

        # Book button
        self.book_passenger_button = ttk.Button(
            self, text="Boka", command=self.master.book_passengers  # type: ignore
        )
        self.book_passenger_button.grid(
            column=0, row=2, sticky="e", padx=5, pady=(10, 0)
        )

        # Finish button
        self.finish_button = ttk.Button(
            self, text="Tillbaka", command=self.master.destroy
        )
        self.finish_button.grid(column=1, row=2, sticky="w", padx=5, pady=(10, 0))
