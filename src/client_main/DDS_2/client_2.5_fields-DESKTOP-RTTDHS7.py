import math
import socket
import threading
import json

from client_main.DDS_2.common_functions import (
    format_msg_with_header,
    format_msg_with_header_and_topic,
    recv_msg,
    recv_topic_data,
    send_config,
    request_constants,
    send_topic_data,
)

# Logging
import logging
import os

file_path = os.path.join(os.path.abspath(os.curdir), "src\\client_main\\LOGS")

FORMAT = "%(levelname)-10s %(asctime)s: %(message)s"
# logging.basicConfig(
#     filename=f"logs_fields.log",
#     encoding="utf-8",
#     level=logging.DEBUG,
#     format=FORMAT,
#     filemode="w",
# )
logging.basicConfig(
    handlers=[
        logging.FileHandler(filename="logs_fields.log", encoding="utf-8", mode="w")
    ],
    level=logging.DEBUG,
    format=FORMAT,
)
# Logging end

HEADERSIZE = 5
CONFIG_DATA = {
    "id": "CLIENT_5",
    "name": "field",
    "subscribed_topics": ["field_update"],
    "published_topics": ["field"],
    "constants_required": [],
    "variables_subscribed": [],
}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect(('192.168.56.1', 1234))

CONSTANTS = {
    "timestepSize": 1,
    "totalTimesteps": 500,
    "requiredThrust": 123_191_000.0,
    "dragCoefficient": 0.75,
    "rocketTotalMass": 7_982_000,
    "rocketUnfuelledMass": 431_000,
    "initialRocketOFMass": 0,
    "O2FRatio": 6,
    "initialOxidiserMass": 0,
    "initialFuelMass": 0,
    "rocketBodyDiameter": 21.3,
    "rocketFrontalArea": 0,
    "specificImpulse": 410,
    "gravitationalAcceleration": 9.81,
    "initialRequiredMassFlowRate": 0,
}

variables = {
    "currentTimestep": 0,
}


def calculate_constants():
    CONSTANTS["initialRocketOFMass"] = (
        CONSTANTS["rocketTotalMass"] - CONSTANTS["rocketUnfuelledMass"]
    )
    CONSTANTS["initialOxidiserMass"] = (
        CONSTANTS["O2FRatio"]
        * CONSTANTS["initialRocketOFMass"]
        / (CONSTANTS["O2FRatio"] + 1)
    )
    CONSTANTS["initialFuelMass"] = CONSTANTS["initialRocketOFMass"] / (
        CONSTANTS["O2FRatio"] + 1
    )
    CONSTANTS["rocketFrontalArea"] = (
        math.pi * CONSTANTS["rocketBodyDiameter"] * CONSTANTS["rocketBodyDiameter"]
    )
    CONSTANTS["initialRequiredMassFlowRate"] = CONSTANTS["requiredThrust"] / (
        CONSTANTS["specificImpulse"] * CONSTANTS["gravitationalAcceleration"]
    )


def process_topic_field(data: str):

    try:
        dataObj: dict = json.loads(data)
        for key in dataObj.keys():
            variables[key] = dataObj[key]
        if dataObj["currentTimestep"] == -1:
            return False
        else:
            return True

    except Exception as e:
        logging.error(e)
    return False


def start_a_cycle():
    logging.info(f"Sending topic 'field' as :{variables=}")
    send_topic_data(server_socket, "field", json.dumps(variables))


def listen_analysis():
    start_a_cycle()
    while True:
        topic, info = recv_topic_data(server_socket)
        if topic == "field_update":
            can_continue = process_topic_field(info)
            if can_continue:
                start_a_cycle()
            else:
                break


# Helper Functions
def send_constants(server_socket: socket.socket):
    global CONSTANTS
    server_socket.send(format_msg_with_header(json.dumps(CONSTANTS)))


def listening_function(server_socket):
    global CONFIG_DATA
    logging.info("Listening while loop started")
    while True:
        try:
            msg = recv_msg(server_socket)
            if msg == "CONFIG":
                send_config(server_socket, CONFIG_DATA)
            elif msg == "CONSTANTS":
                send_constants(server_socket)
            elif msg == "START":
                break
        except Exception as e:
            print(f"Error Occured\n{e}")
            break
    listen_analysis()


def main():
    calculate_constants()
    listening_thread = threading.Thread(
        target=listening_function, args=(server_socket,)
    )

    listening_thread.start()


if __name__ == "__main__":
    try:
        main()
    except:
        server_socket.close()
