import sys
from typing import NoReturn
from biljettbokning.app import App


def launch() -> NoReturn:
    app = App()
    app.mainloop()
    sys.exit(1)


if __name__ == "__main__":
    launch()
