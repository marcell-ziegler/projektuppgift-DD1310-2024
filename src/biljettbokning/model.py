"""Data model for train booking system"""

from datetime import datetime, timedelta
import itertools
import os
from pathlib import Path
import json
import pickle
import random
import re
import math
from typing import Optional


class Seat:
    """A seat in a Carriage with a number and an optional passenger name.

    Attributes:
        number (int): The seat number
        passenger_name (str): The name of the passenger in the seat (default: "")

    Instance methods:
        is_booked() -> bool: Return if the seat is booked
        unbook() -> None: Remove the passenger from the seat
    """

    def __init__(self, number: int, passenger_name: Optional[str] = None):
        """Make a new seat with the specified number and if applicable the passenger name (default: "")."""
        self.number = number
        self.passenger_name = passenger_name

    def is_booked(self) -> bool:
        """Return True if there is a passenger in the seat, else False."""
        return bool(self.passenger_name)

    def unbook(self) -> None:
        self.passenger_name = None

    def __repr__(self):
        return str(self.number) if not self.is_booked() else "*" * len(str(self.number))


class Carriage:
    """Holds all seats of a carriage in the specified configuration

    Attributes:
        number (int): The carriage number
        seating_configuration (str): The seating config as 'x+y' where 0 <= x,y <= 9 for x,y: int
        num_rows (int): The number of rows in the carriage
        seats (list[tuple[list[Seat], list[Seat]]]): A list of tuples where each tuple contains a list of left and right seats in a row
        num_left_seats (int): The number of seats on the left side of the carriage
        num_right_seats (int): The number of seats on the right side of the carriage
        total_seats (int): sum of all seats in the car
        total_seats_in_row (int): sum of left_seats + right_seats

    Instance methods:
        get_seat_num(seat_num: int) -> Seat: Return the seat object for the given seat number in the carriage
        get_seat_name(passenger_name: str) -> Seat: Return the seat object for the given passenger name in the carriage
        book_passenger(name: str, seat_num: int) -> None: Books a passenger into the specified seat number
    """  # noqa pylint: disable=line-too-long

    def __init__(self, seating_configuration: str, num_rows: int):
        """Create a new empty carriage with the specified seating configuration.

        Args:
            seating_configuration (str): seating_configuration in the format 'x+y' where 0 <= x,y <= 9 for x,y: int
            num_rows (int): The number of rows in the carriage
        """  # noqa
        self.seating_configuration = seating_configuration
        self.num_rows = num_rows

        # Create seats
        self.num_left_seats, self.num_right_seats = (
            int(val) for val in seating_configuration.split("+")
        )

        self.total_seats_in_row = self.num_left_seats + self.num_right_seats

        # Populate the seats list with seat objects in ascending order
        self.seats: list[tuple[list[Seat], list[Seat]]] = []

        seat_num = 0
        # Populate the seat list with ascending numbers
        for _ in range(num_rows):
            left = []
            for _ in range(self.num_left_seats):
                seat_num += 1
                left.append(Seat(seat_num))

            right = []
            for _ in range(self.num_right_seats):
                seat_num += 1
                right.append(Seat(seat_num))
            self.seats.append((left, right))

        self.total_seats = len(self._flat_seats)

    @property
    def seating_configuration(self) -> str:
        """Seating configuration in the format 'x+y' where 0 <= x,y <= 9 for x,y: int"""
        return self._seating_configuration

    @seating_configuration.setter
    def seating_configuration(self, value):
        # Validate type
        if not isinstance(value, str):
            raise TypeError("Seating configuration must be a string")

        # Validate format to the property definition
        if re.match(r"^\d\+\d$", value) is None:
            raise ValueError(
                "Invalid seating configuration. Correct examples: '1+2', '3+2', '2+2' etc."
            )

        self._seating_configuration = value

    @property
    def _flat_seats(self) -> list[Seat]:
        """Return a flat list of all seats in the carriage"""
        return list(itertools.chain(*itertools.chain(*self.seats)))

    @property
    def remaining_seats(self) -> int:
        """Number of seats were seat.is_booked => False"""
        return self.total_seats - len(
            list(filter(lambda s: s.is_booked(), self._flat_seats))
        )

    def get_seat_num(self, seat_num: int) -> Seat:
        """Return the seat object for the given seat number in the carriage

        Args:
            seat_num (int): The seat number

        Returns:
            Seat: The seat object for the seat number

        Raises:
            IndexError: If the seat number is invalid
        """
        if seat_num < 1 or seat_num > len(self._flat_seats):
            raise IndexError(f"Invalid seat number {seat_num}")

        # Total row width
        row_width = self.total_seats_in_row

        # Get row by rounding up to the nearest integer row based on the index
        row = math.ceil(seat_num / row_width)

        # Get the index of the seat in the row
        # row_width * (row - 1) is the number of seats in the previous rows to be removed
        row_index = seat_num - row_width * (row - 1)

        # Check is seat is on left side
        if row_index <= self.num_left_seats:
            return self.seats[row - 1][0][row_index - 1]

        # Seat is on the right side, index subtracts left seats to fit within
        # the right side tuple

        return self.seats[row - 1][1][row_index - 1 - self.num_left_seats]

    def get_seat_name(self, passenger_name: str) -> Seat:
        """Return the seat object for the given passenger name in the carriage

        Args:
            passenger_name (str): The name of the passenger

        Returns:
            Seat: The seat object for the passenger

        Raises:
            KeyError: If no seat is found for the passenger
            ValueError: If multiple seats are found for the passenger
        """

        # Get all matches
        seat_filter = filter(
            lambda s: s.passenger_name == passenger_name,
            self._flat_seats,
        )

        # Unpack iterator
        matches = list(seat_filter)

        if len(matches) < 1:
            raise KeyError(f"No seat found for passenger {passenger_name}")
        if len(matches) > 1:
            raise ValueError(f"Multiple seats found for passenger {passenger_name}")

        # Only one match possible, return
        return matches[0]

    def book_passenger(self, name: str, seat_num: int) -> None:
        """Books a passenger into the specified seat number.

        Args:
            name (str): The name of the passenger
            seat_num (int): The seat number to book the passenger into

        Raises:
            IndexError: If the seat number is invalid
            ValueError: If the seat is already booked
        """

        try:
            # Get seat to be booked
            seat = self.get_seat_num(seat_num)
        except IndexError as e:
            raise IndexError(f"Invalid seat number {seat_num}") from e

        # Check booking status
        if seat.is_booked():
            raise ValueError(f"Seat {seat_num} is already booked")

        # Perform booking
        seat.passenger_name = name

    def __str__(self):
        return f"Carriage: {self.seating_configuration} with {self.num_rows} rows"


class Train:
    """Represents a train with carriages, a number and destination and arrival times and cities respectively."""  # noqa

    DESTINATIONS = [
        "Stockholm C",
        "Uppsala C",
        "Bålsta",
        "Märsta",
        "Knivsta",
        "Södertälje Syd",
        "Göteborg C",
        "Malmö C",
        "Skövde C",
        "Linköping",
        "Norrköping",
        "Motala",
        "Gävle C",
        "Ljusdal",
        "Åre",
        "Härnösand",
        "Kristianstad",
        "Karstad",
    ]

    RANDOM_HOUR_TIMEDELTA_RANGE = (0, 72)

    RANDOM_ARRIVAL_HOUR_TIMEDELTA_RANGE = (1, 5)

    def __init__(
        self,
        number: int,
        departure: datetime,
        arrival: datetime,
        start: str,
        dest: str,
        carriages: Optional[list[Carriage]] = None,
    ):
        """Make new Train.

        Args:
            number (int): Unique train number
            departure (datetime): Departure time
            arrival (datetime): Arrival time
            start (str): Starting city
            dest (str): Destination city
            carriages (Optional[list[Carriage]], optional): Carriages to be added if applicable. Defaults to None.
        """  # noqa
        self.number = number
        self.departure = departure
        self.arrival = arrival
        self.start = start
        self.dest = dest
        self.carriages: list[Carriage] = carriages if carriages is not None else []

    def book_passenger(
        self, carriage: int, seat_number: int, passenger_name: str
    ) -> None:
        """Book a passenger into the specified seat in the specified carriage.

        Args:
            carriage (int): The carriage index the seat is in
            seat_number (int): The seat number within the carriage
            passenger_name (str): The name of the passenger

        Raises:
            ValueError: If seat is already booked
            IndexError: If carriage number and/or seat number is invalid
        """

        car = self.carriages[carriage]
        car.book_passenger(passenger_name, seat_number)

    def unbook_passenger(self, carriage_num: int, name: str) -> None:
        """Unbook a passenger with the specified name from the specified carriage.

        Args:
            carriage (int): Carriage index to be unbooked from
            name (str): Name of passenger to be unbooked

        Raises:
            KeyError: If no seat is found for the specified passenger
            ValueError: If multiple matches found
            IndexError: If carriage num is out of range
        """

        # Try to get appropriate seat and unbook, get_seat_name raises errors on failure
        seat = self.carriages[carriage_num].get_seat_name(name)
        seat.unbook()

    def unbook_seat(self, carriage_num: int, seat_num: int) -> None:
        """Unbook the specified seat in the given carriage.

        Args:
            carriage_num (int): Number of the carriage
            seat_num (int): Seat to be unbooked

        Raises:
            IndexError: If seat does not exist or carriage num out of range
        """
        # Try removing, invalid seat raises error from get_seat_num
        self.carriages[carriage_num].get_seat_num(seat_num).unbook()

    def __lt__(self, other) -> bool:
        """Comapare based on departure time."""
        # Only supported for Train-Train comparison
        if not isinstance(other, Train):
            raise TypeError("Only supported for values of type Train.")
        return self.departure < other.departure

    def serialize(self, root_path: str) -> None:
        """Serializes the train to a directory named train_n where n is Train.number.

        Directory structure:
        root_path
            - train_n
                -train.json
                -carriage_1.pickle
                -carriage_2.pickle
                -carriage_3.pickle
                ...
                -carriage_n.pickle

        Args:
            root_path (str): Path to root directory
        """
        root = Path(root_path)

        if root == Path.cwd():
            # In case the user cancels save, return
            return

        # Make a dict representing the train
        # "carriages" is a list of paths to the carriage pickle files
        repr_dict = {
            "number": self.number,
            "departure": self.departure.isoformat(),
            "arrival": self.arrival.isoformat(),
            "start": self.start,
            "dest": self.dest,
            "num_carriages": len(self.carriages),
        }

        # make a dir for this specific train
        train_dir = root / f"train_{self.number}"
        if train_dir.exists():
            os.system(
                ("rmdir /s /q " if os.name == "nt" else "rmdir -r ") + str(train_dir)
            )
        os.mkdir(train_dir)

        # append appropriate paths and pickle carriage to appropriate file
        for i, carriage in enumerate(self.carriages):
            carriage_path = train_dir / f"carriage_{i}.pickle"

            with open(carriage_path, "wb") as f:
                pickle.dump(carriage, f)

        # dump the dict
        with open(train_dir / "train.json", "w", encoding="utf-8") as f:
            json.dump(repr_dict, f)

    def menu_text(self) -> str:
        """Get text representation for menu."""
        return f"Tåg {self.number}: {self.departure.time().isoformat("minutes")} {self.start}  ->  {self.arrival.time().isoformat("minutes")} {self.dest}"  # noqa

    def __repr__(self):
        return f"Train ({self.number})"

    @staticmethod
    def random(num: int):
        """Make random train object.

        Args:
            num (int): Unique train number.
        """
        departure = datetime.now() + timedelta(
            hours=random.randint(*Train.RANDOM_HOUR_TIMEDELTA_RANGE),
            minutes=random.randint(0, 60),
        )
        arrival = departure + timedelta(
            hours=random.randint(*Train.RANDOM_ARRIVAL_HOUR_TIMEDELTA_RANGE),
            minutes=random.randint(0, 60),
        )

        start_dest = random.sample(Train.DESTINATIONS, 2)

        carriages: list[Carriage] = []
        # Picka  seating configuration for the train
        config = random.choice(["2+2", "3+2", "2+3", "3+3"])

        for _ in range(random.randint(3, 5)):
            carriages.append(Carriage(config, random.randint(7, 13)))

        return Train(num, departure, arrival, start_dest[0], start_dest[1], carriages)

    @staticmethod
    def from_file(directory_path: str):
        """Load train for the specified serialization directory."""
        path = Path(directory_path)

        # Get train repr dict
        with open(path / "train.json", "r", encoding="utf-8") as f:
            repr_dict: dict = json.load(f)

        # Remove carriage amount
        num_carriages = repr_dict.pop("num_carriages")

        # Convert times back into objects
        repr_dict["departure"] = datetime.fromisoformat(repr_dict["departure"])
        repr_dict["arrival"] = datetime.fromisoformat(repr_dict["arrival"])

        # Make train with the correct values
        train = Train(**repr_dict)

        for i in range(num_carriages):
            # Unpickle carriages and load into train
            with open(path / f"carriage_{i}.pickle", "rb") as f:
                train.carriages.append(pickle.load(f))

        return train

    def terminal_repr(self) -> str:
        """Representation for terminal and main menu."""
        # Dim 0: each car
        # Dim 1: lines in the cars repr
        cars: list[list[str]] = []

        # Repeat generation for each car
        for car_num, car in enumerate(self.carriages):
            # Top dashed line
            car_str = []
            # add all seats to the left
            for col in range(car.num_left_seats):
                col_str = "| "
                for row in range(car.num_rows):
                    col_str += f"{car.seats[row][0][col]}{" " if car.seats[row][0][col].number < 10 else ""} "
                col_str += "|"
                car_str.append(col_str)

            # Middle divider
            car_str.append("|" + " " * (len(car_str[0]) - 2) + "|")

            # Repeat for right seats
            for col in range(car.num_right_seats):
                col_str = "| "
                for row in range(car.num_rows):
                    col_str += f"{car.seats[row][1][col]}{" " if car.seats[row][1][col].number < 10 else ""} "
                col_str += "|"
                car_str.append(col_str)

            # Bottom line
            car_str.append("-" * (len(car_str[0])))

            # Make a row of spaces with carriage number in it
            number_row = (" " * (len(car_str[0]) // 2 - 2)) + str(car_num + 1) + "."
            number_row += " " * (len(car_str[0]) - len(number_row))

            # add the number row and the top line to the list
            car_str = [number_row, "-" * (len(car_str[0]))] + car_str
            cars.append(car_str)

        # Concatenate everything
        result_str_lines = []
        for col in range(len(cars[0])):
            line = ""
            for car in cars:
                line += car[col] + "  "
            result_str_lines.append(line)

        result_str = ""
        for line in result_str_lines:
            result_str += line + "\n"

        return result_str


class Booking:
    """A seat ticket booking abstraction for printing purposes."""

    def __init__(self, name: str, seat_num: int, carriage_num: int, train: Train):
        self.name = name
        self.seat = seat_num
        self.carriage = carriage_num
        self.train = train

    def __str__(self):
        """Get representation for file or terminal printing."""

        # Add all lines with only information
        lines = [
            "Platsbiljett",
            f"Tåg {self.train.number}",
            "",
            f"den {self.train.departure.date().isoformat()}",
            "",
            f"{self.train.departure.time().isoformat("minutes")} {self.train.start}",
            "|",
            "|",
            "v",
            f"{self.train.arrival.time().isoformat("minutes")} {self.train.dest}",
            "",
            f"{self.name}",
            f"Plats {self.seat}, vagn {self.carriage}",
            "",
            r"                   =%%%%%*   %%%                 ",
            r"                 :%%#        %%%                 ",
            r"                 +%%%.       %%%                 ",
            r"                  -%%%%%%-   %%%                 ",
            r"                      +%%%#  %%%                 ",
            r"                       =%%+  %%%                 ",
            r"                  %%%%%%%:  #%%=                 ",
            r"                          :+=-                   ",
            r"  :%%%%%%%%%%%%%%#=            *%%%%%%%%%%%%%%%  ",
            r"    :++++++++**#%%%%.        #%%%%#**++++++++    ",
            r"                 .%%%        %%*                 ",
            r"       %%%%%%%%%:  *%       -%   #%%%%%%%%:      ",
            r"         -===#%%%*  :        .  %%%%+===:        ",
            r"              =%%%#           :%%%%              ",
            r"               .%%%%%+     .#%%%%#               ",
            r"                 .%%%%%%%%%%%%%#                 ",
            r"                     -*###**.                    ",
        ]

        # The longest line
        max_length = max(len(s) for s in lines)
        # Add spaces to center everything based on max_length
        for i, line in enumerate(lines):
            first_half = " " * ((max_length - len(line)) // 2) + line
            lines[i] = first_half + " " * (max_length - len(first_half))

        return "\n".join(lines)

    def __eq__(self, other):
        """Check equality with other Booking for removal purposes."""
        # Only works for other Bookings
        if not isinstance(other, Booking):
            return False

        # If all true, they must be equal
        return all(
            [
                self.carriage == other.carriage,
                self.seat == other.seat,
                self.name == other.name,
                self.train.number == other.train.number,
            ]
        )


class Bookings:
    """Custom list for bookings to implement removal logic.

    Instance Methods:
        append(item: Booking): same as list.append
        remove(train_num: int, carriage_num: int, seat_num: int): Remove booking with specified attributes, if it exists. Otherwise fail silently.
    """  # noqa

    def __init__(self):
        """Make empty booking list."""
        self._bookings: list[Booking] = []

    def append(self, item: Booking):
        """Add a Booking object."""
        self._bookings.append(item)

    def remove(self, train_num: int, carriage_num: int, seat_num: int):
        """Remove a Booking object that matches the criteria.

        carriage_num starts from 1

        Args:
            train_num (int): train_number
            carriage_num (int): carriage number (starts 1)
            seat_num (int): seat number (starts 1)

        Raises:
            ValueError: if more than one seat is found for the criteria (double booking)
        """
        matching_trains = list(
            filter(lambda b: b.train.number == train_num, self._bookings)
        )
        matching_carriages = list(
            filter(lambda b: b.carriage == carriage_num, matching_trains)
        )
        matching_seats = list(filter(lambda b: b.seat == seat_num, matching_carriages))

        # Only single matches allowed with same train-carriage combo
        if len(matching_seats) > 1:
            raise Bookings.MultipleError()
        if len(matching_seats) < 1:
            raise ValueError("No bookings with the specified parameter!")

        # Find and remove the single match
        self._bookings.remove(matching_seats[0])

    class MultipleError(Exception):
        """Exception raised if there are more than one bookings with the same seat."""

        def __init__(self, message="More than one booking with the same seat!"):
            self.message = message
            super().__init__(self.message)

    def __getitem__(self, index: int) -> Booking:
        return self._bookings[index]

    def __setitem__(self, index: int, value: Booking):
        self._bookings[index] = value

    def __delitem__(self, index: int):
        del self._bookings[index]

    def __len__(self) -> int:
        return len(self._bookings)

    def __iter__(self):
        return iter(self._bookings)

    def __str__(self):
        return "\n\n".join(str(b) for b in self._bookings)
