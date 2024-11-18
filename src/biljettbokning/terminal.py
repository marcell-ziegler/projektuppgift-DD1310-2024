from datetime import datetime
from math import ceil
import os
import sys
from time import sleep
from typing import NoReturn

import pandas as pd

from biljettbokning.model import Carriage, Train


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def boka(trains):
    print("boka")


def avboka(trains):
    print("avboka")


def skriv_biljetter(trains):
    print("skriv_biljett")


def menu(trains) -> NoReturn:
    clear()
    while True:
        print(
            """Gör ett val:
            1. (B)oka
            2. (A)vboka
            3. (S)kriv biljetter
            4. Avsluta"""
        )
        val = input("Val>").upper()
        match val:
            case "1" | "B":
                clear()
                boka(trains)
            case "2" | "A":
                clear()
                avboka(trains)
            case "3" | "S":
                clear()
                skriv_biljetter(trains)
            case "4":
                clear()
                sleep(0.2)
                sys.exit(0)
            case _:
                clear()
                print("Ogiltigt val, försök igen!")
                sleep(0.8)
                continue


if __name__ == "__main__":
    trains: list[Train] = []
    data = pd.read_excel("test/tåg.xlsx")

    for i, train in data.iterrows():
        trains.append(
            Train(
                train["Number"],
                datetime.fromisoformat(train["Departure"]),
                datetime.fromisoformat(train["Arrival"]),
                train["Start"],
                train["Destination"],
                [
                    Carriage("2+2", ceil(train["Seats"] / 4))
                    for _ in range(train["Carriages"])
                ],
            )
        )

    # menu()
