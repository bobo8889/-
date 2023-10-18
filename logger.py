
from datetime import datetime
from sys import exit


def println(log: str) -> None:
    time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print("%s %s" % (time, log))


def fatalln(log: str) -> None:
    println(log)
    exit(1)
