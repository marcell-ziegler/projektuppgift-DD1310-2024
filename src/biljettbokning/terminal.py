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

    def boka(self):
        print("Välj tåg:")
        for i, train in enumerate(self.trains):
            print(f"{i+1}. Tåg {train.number}: {train.start} -> {train.dest}")
        choice = int(input("Val>"))
        selected = self.trains[choice - 1]
        print(selected.terminal_repr())
        input()
        return

    def avboka(self):
        print("avboka")

    def skriv_biljetter(self):
        print("skriv_biljett")

    def menu(self) -> NoReturn:
        self.clear()
        while True:
            print(
                """Gör ett val:
                1. (B)oka
                2. (A)vboka
                3. (S)kriv biljetter
                4. Avsluta"""
            )
            val = input("Val>").upper()
            self.clear()
            match val:
                case "1" | "B":
                    self.boka()
                case "2" | "A":
                    self.avboka()
                case "3" | "S":
                    self.skriv_biljetter()
                case "4":
                    sleep(0.2)
                    sys.exit(0)
                case _:
                    print("Ogiltigt val, försök igen!")
                    sleep(0.8)
                    continue


if __name__ == "__main__":
    t = Train.from_file("./trains/train_1")
    term = Terminal([t])
    term.menu()
