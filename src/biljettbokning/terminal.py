import os
import sys
from time import sleep
from typing import NoReturn


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def boka():
    print("boka")


def avboka():
    print("avboka")


def skriv_biljetter():
    print("skriv_biljett")


def menu() -> NoReturn:
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
                boka()
            case "2" | "A":
                clear()
                avboka()
            case "3" | "S":
                clear()
                skriv_biljetter()
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
    menu()
