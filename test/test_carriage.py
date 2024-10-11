import itertools
from biljettbokning.model import Carriage
import pytest


class TestCarriage:
    def test_create_carriage(self):
        carriage = Carriage("2+2", 5, 10)
        assert carriage.number == 10
        assert carriage.num_rows == 5
        assert carriage.left_seats == 2
        assert carriage.right_seats == 2
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
