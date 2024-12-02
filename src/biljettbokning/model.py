"""Data model for train booking system"""

from datetime import datetime
import itertools
import os
from pathlib import Path
import json
import pickle
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
    """

    def __init__(self, number: int, passenger_name: Optional[str] = None):
        """Make a new seat with the specified number and if applicable the passenger name (default: "")."""
        self.number = number
        self.passenger_name = passenger_name

    def is_booked(self) -> bool:
        """Return True if there is a passenger in the seat, else False."""
        return bool(self.passenger_name)

    def __repr__(self):
        return str(self.number) if not self.is_booked() else "*"


class Carriage:
    """Holds all seats of a carriage in the specified configuration

    Attributes:
        number (int): The carriage number
        seating_configuration (str): The seating config as 'x+y' where 0 <= x,y <= 9 for x,y: int
        num_rows (int): The number of rows in the carriage
        seats (list[tuple[list[Seat], list[Seat]]]): A list of tuples where each tuple contains a list of left and right seats in a row
        num_left_seats (int): The number of seats on the left side of the carriage
        num_right_seats (int): The number of seats on the right side of the carriage

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

        # Create seants

        self.num_left_seats, self.num_right_seats = (
            int(val) for val in seating_configuration.split("+")
        )

        self.total_seats = self.num_left_seats + self.num_right_seats

        # Populate the seats list with seat objects in ascending order
        self.seats: list[tuple[list[Seat], list[Seat]]] = []

        seat_num = 0
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
        row_width = self.total_seats

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

        seat_filter = filter(
            lambda s: s.passenger_name == passenger_name,
            self._flat_seats,  # Flatten the list of seats
        )

        matches = list(seat_filter)

        if len(matches) < 1:
            raise KeyError(f"No seat found for passenger {passenger_name}")
        elif len(matches) > 1:
            raise ValueError(f"Multiple seats found for passenger {passenger_name}")

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
            seat = self.get_seat_num(seat_num)
        except IndexError as e:
            raise IndexError(f"Invalid seat number {seat_num}") from e

        if seat.is_booked():
            raise ValueError(f"Seat {seat_num} is already booked")

        seat.passenger_name = name

    def __str__(self):
        return f"Carriage: {self.seating_configuration} with {self.num_rows} rows"


class Train:
    def __init__(
        self,
        number: int,
        departure: datetime,
        arrival: datetime,
        start: str,
        dest: str,
        carriages: Optional[list[Carriage]] = None,
    ):
        self.number = number
        self.departure = departure
        self.arrival = arrival
        self.start = start
        self.dest = dest
        self.carriages: list[Carriage] = carriages if carriages is not None else []

    def __lt__(self, other) -> bool:
        if not isinstance(other, Train):
            raise TypeError("Only supported for values of type Train.")
        return self.departure < other.departure

    def serialize(self, root_path: Optional[str]) -> None:
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
        """
        root = Path(root_path) if root_path else Path.cwd()

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

    def __repr__(self):
        return f"""Train ({self.number}):
            \tDeparture: {self.departure}
            \tArrival: {self.arrival}
            \tStart: {self.start}
            \tDestination: {self.dest}
            \tNumber of carriages: {len(self.carriages)}
            \tSeats per carriage: {len(self.carriages[0]._flat_seats)}"""

    @staticmethod
    def from_file(directory_path: str):
        """Load train for the specified serialization directory"""
        path = Path(directory_path)

        with open(path / "train.json", "r", encoding="utf-8") as f:
            repr_dict: dict = json.load(f)

        num_carriages = repr_dict.pop("num_carriages")
        train = Train(**repr_dict)

        for i in range(num_carriages):
            with open(path / f"carriage_{i}.pickle", "rb") as f:
                train.carriages.append(pickle.load(f))

        return train

    def terminal_repr(self) -> str:
        # Dim 0: each car
        # Dim 1: lines in the cars repr
        cars: list[list[str]] = []

        # Repeat generation for each car
        for car in self.carriages:
            # Top dashed line
            car_str = ["-" * (car.num_rows * 3 + 3)]
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
            car_str.append("-" * (car.num_rows * 3 + 3))
            cars.append(car_str)

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
