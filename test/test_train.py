from datetime import datetime, time, timedelta
import random
from biljettbokning.model import Train


class TestTrain:
    def test_create(self):
        t = Train(
            152,
            datetime(2024, 5, 22, 15, 32),
            datetime(2024, 5, 22, 16, 45),
            "sthlm",
            "gbg",
        )
        assert t.number == 152
        assert t.departure == datetime(2024, 5, 22, 15, 32)
        assert t.arrival == datetime(2024, 5, 22, 16, 45)
        assert t.start == "sthlm"
        assert t.dest == "gbg"

    def test_compare(self):
        t1 = Train(
            152,
            datetime(2024, 5, 22, 15, 32),
            datetime(2024, 5, 22, 16, 45),
            "sthlm",
            "gbg",
        )
        t2 = Train(
            152,
            datetime(2024, 5, 22, 16, 32),
            datetime(2024, 5, 22, 16, 45),
            "sthlm",
            "gbg",
        )
        assert t1 < t2
        assert t2 > t1

    def test_sort(self):
        ts = []
        for i in range(5):
            ts.append(
                Train(
                    i,
                    datetime(2024, 5, 22, 12, 0) + timedelta(hours=i),
                    datetime(2024, 6, 22, 13, 0) + timedelta(hours=i),
                    "sthlm",
                    "gbg",
                )
            )
        assert all(ts[i] < ts[i + 1] for i in range(len(ts) - 1))
        random.shuffle(ts)
        assert not all(ts[i] < ts[i + 1] for i in range(len(ts) - 1))
        ts.sort()
        assert all(ts[i] < ts[i + 1] for i in range(len(ts) - 1))
