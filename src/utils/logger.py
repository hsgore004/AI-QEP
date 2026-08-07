import json
from datetime import datetime


class Logger:

    WIDTH = 100

    @staticmethod
    def _time():
        return datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def section(title: str):

        print()
        print("=" * Logger.WIDTH)
        print(f"[{Logger._time()}] {title.upper()}")
        print("=" * Logger.WIDTH)

    @staticmethod
    def subsection(title: str):

        print()
        print("-" * Logger.WIDTH)
        print(title)
        print("-" * Logger.WIDTH)

    @staticmethod
    def text(value):

        if value is None:
            print("<None>")
        else:
            print(value)

    @staticmethod
    def json(value):

        print(json.dumps(value, indent=4, ensure_ascii=False))

    @staticmethod
    def line():

        print("-" * Logger.WIDTH)

    @staticmethod
    def blank():

        print()

    @staticmethod
    def success(message: str):

        print(f"[✓] {message}")

    @staticmethod
    def warning(message: str):

        print(f"[!] {message}")

    @staticmethod
    def error(message: str):

        print(f"[X] {message}")