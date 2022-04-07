import logging
import sys

FORMAT = "%(levelname)-10s %(asctime)s: %(message)s"
logging.basicConfig(
    filename="example.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format=FORMAT,
)
print(logging.debug("This message should go to the log \nfile"))
print(logging.info("So should this"))
print(logging.warning("And this, too"))
print(logging.error("And non-ASCII stuff, too, like resund and Malm"))
