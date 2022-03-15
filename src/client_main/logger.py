import datetime
import time

LOGS = f"Logs for Simulation\n{'Start Time':<15}:{datetime.datetime.now()}\n\n"

types = ["INFO", "ERROR", "WARNING"]


def add_log(log_type: str, msg: str):
    global LOGS

    if log_type not in types:
        log_type = "INFO"
    LOGS += f"{log_type:<10}: {str(datetime.datetime.now()):25} - {msg}\n"


def write_log():
    global LOGS
    LOGS += f"\n\nSimulation Ended\n{'End Time':<15}:{datetime.datetime.now()}"
    timestamp = str(datetime.datetime.now()).replace(" ", "_").replace(":", "-")
    # TODO COMMENT THIS OUT LATER
    timestamp = ""
    with open(f"logs_{timestamp}.txt", mode="w") as log_file:
        log_file.write(LOGS)
