import itertools
import pytest
from biljettbokning.model import Carriage


class TestCarriage:
    def test_create_carriage(self):
        # pylint: disable=protected-access
        carriage = Carriage("2+2", 5, 10)
        assert carriage.number == 10
        assert carriage.num_rows == 5
        assert carriage.num_left_seats == 2
        assert carriage.num_right_seats == 2
        assert len(carriage._flat_seats) == (2 + 2) * 5
        assert (
            len(list(itertools.chain(*itertools.chain(*carriage.seats)))) == (2 + 2) * 5
        )

    def test_incorrect_seat_configuration(self):
        with pytest.raises(ValueError):
            Carriage("a+3", 5, 10)

        with pytest.raises(ValueError):
            Carriage("3+b", 5, 10)

        with pytest.raises(ValueError):
            Carriage("15+15", 5, 10)

        with pytest.raises(ValueError):
            Carriage("3+3+3", 5, 10)

        with pytest.raises(ValueError):
            Carriage("3", 5, 10)

    def test_num_search(self):
        rows = 5
        carriage = Carriage("2+2", rows, 10)
        for i in range(rows):
            assert carriage.get_seat_num(i * (2 + 2) + 1) is carriage.seats[i][0][0]
            assert carriage.get_seat_num(i * (2 + 2) + 2) is carriage.seats[i][0][1]
            assert carriage.get_seat_num(i * (2 + 2) + 3) is carriage.seats[i][1][0]
            assert carriage.get_seat_num(i * (2 + 2) + 4) is carriage.seats[i][1][1]

        carriage = Carriage("2+3", rows, 10)
        for i in range(rows):
            assert carriage.get_seat_num(i * (2 + 3) + 1) is carriage.seats[i][0][0]
            assert carriage.get_seat_num(i * (2 + 3) + 2) is carriage.seats[i][0][1]
            assert carriage.get_seat_num(i * (2 + 3) + 3) is carriage.seats[i][1][0]
            assert carriage.get_seat_num(i * (2 + 3) + 4) is carriage.seats[i][1][1]
            assert carriage.get_seat_num(i * (2 + 3) + 5) is carriage.seats[i][1][2]

        carriage = Carriage("1+3", rows, 10)
        for i in range(rows):
            assert carriage.get_seat_num(i * (1 + 3) + 1) is carriage.seats[i][0][0]
            assert carriage.get_seat_num(i * (1 + 3) + 2) is carriage.seats[i][1][0]
            assert carriage.get_seat_num(i * (1 + 3) + 3) is carriage.seats[i][1][1]
            assert carriage.get_seat_num(i * (1 + 3) + 4) is carriage.seats[i][1][2]

        for i in [200, 0, -1, -300, -20]:
            with pytest.raises(IndexError):
                carriage.get_seat_num(i)

    def test_booking(self):
        carriage = Carriage("2+2", 5, 10)

        seat = carriage.get_seat_num(1)
        carriage.book_passenger("John Doe", 1)

        assert seat.passenger_name == "John Doe"

        seat = carriage.get_seat_num(20)
        carriage.book_passenger("Jane Doe", 20)

        assert seat.passenger_name == "Jane Doe"

        with pytest.raises(ValueError):
            carriage.book_passenger("Jane Doe", 20)

        with pytest.raises(ValueError):
            carriage.book_passenger("John Doe", 20)

        for i in [200, 0, -1, -300, -20]:
            with pytest.raises(IndexError):
                carriage.book_passenger("John Doe", i)

    def test_name_search(self):
        carriage = Carriage("2+2", 5, 10)
        letters = "abcdfghijklmnopqrstu"

        nums = list(range(1, 21))

        for letter, num in zip(list(letters), list(nums)):
            seat = carriage.get_seat_num(num)
            seat.passenger_name = letter

        for letter in letters:
            seat = carriage.get_seat_name(letter)
            assert seat.passenger_name == letter
