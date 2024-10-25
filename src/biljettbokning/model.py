"""Data model for train booking system"""

import itertools
import re
import math


class Seat:
    def __init__(self, number: int, passenger_name: str = ""):
        self.number = number
        self.passenger_name = passenger_name

    def __repr__(self):
        return str(self.number)


class Carriage:
    """Holds all seats of a carriage in the specified configuration"""

    def __init__(self, seating_configuration: str, num_rows: int, carriage_num: int):

        self.number = carriage_num
        self.seating_configuration = seating_configuration
        self.num_rows = num_rows

        # Create seants

        self.num_left_seats, self.num_right_seats = (
            int(val) for val in seating_configuration.split("+")
        )

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
        """Return the seat object for the given seat number in the carriage"""
        # Total row width
        row_width = self.num_left_seats + self.num_right_seats

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

        if len(matches) > 1:
            raise ValueError(f"Multiple seats found for passenger {passenger_name}")

        return matches[0]

    def __str__(self):
        return f"Carriage: {self.seating_configuration} with {self.num_rows} rows"


class Train:
    def __init__(self, name: str, carriages: Optional[list[Carriage]] = None):
        self.name = name
        self.carriages = carriages if carriages is not None else []
