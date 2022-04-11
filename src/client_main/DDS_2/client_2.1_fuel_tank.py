import socket
import threading
import json

from client_main.DDS_2.common_functions import (
    check_to_run_cycle,
    field_received,
    format_msg_with_header,
    make_all_cycle_flags_default,
    recv_msg,
    recv_topic_data,
    send_config,
    request_constants,
    send_topic_data,
    thrust_received,
)

# Logging
import logging
import os


file_path = os.path.join(os.path.abspath(os.curdir), "src\\client_main\\LOGS")

FORMAT = "%(levelname)-10s %(asctime)s: %(message)s"
logging.basicConfig(
    filename=f"logs_fuel_tank.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format=FORMAT,
    filemode="w",
)

# Logging end

HEADERSIZE = 5
CONFIG_DATA = {
    "id": "CLIENT_1",
    "name": "fuel_tank",
    "subscribed_topics": ["thrust", "field"],
    "published_topics": ["fuel_flow"],
    "constants_required": [
        "specificImpulse",
        "gravitationalAcceleration",
        "O2FRatio",
        "initialOxidiserMass",
        "initialFuelMass",
        "rocketTotalMass",
        "timestepSize",
        "totalTimesteps",
    ],
    "variables_subscribed": [],
}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect((socket.gethostname(), 1234))

CONSTANTS = {}

topic_data = {
    "currentMassFlowRate": 0,
    "currentOxidiserMass": 0,
    "currentFuelMass": 0,
    "currentRocketTotalMass": 0,
}
cycle_flags = {"thrust": False, "field": False}
topic_func_dict = {"thrust": thrust_received, "field": field_received}

# to store data received
data_dict = {}


def fill_init_topic_data():
    global topic_data
    global data_dict
    topic_data["currentOxidiserMass"] = CONSTANTS["initialOxidiserMass"]
    topic_data["currentFuelMass"] = CONSTANTS["initialFuelMass"]
    topic_data["currentRocketTotalMass"] = CONSTANTS["rocketTotalMass"]

    data_dict["currentMassFlowRate"] = 0
    data_dict["currentOxidiserMass"] = CONSTANTS["initialOxidiserMass"]
    data_dict["currentFuelMass"] = CONSTANTS["initialFuelMass"]
    data_dict["currentRocketTotalMass"] = CONSTANTS["rocketTotalMass"]


# Actual Analysis
def run_one_cycle():
    global data_dict
    data_dict["currentMassFlowRate"] = data_dict["currentThrust"] / (
        CONSTANTS["specificImpulse"] * CONSTANTS["gravitationalAcceleration"]
    )
    topic_data["currentMassFlowRate"] = data_dict["currentMassFlowRate"]

    massReduced = data_dict["currentMassFlowRate"] * CONSTANTS["timestepSize"]
    data_dict["currentOxidiserMass"] = data_dict["currentOxidiserMass"] - (
        massReduced * CONSTANTS["O2FRatio"] / (CONSTANTS["O2FRatio"] + 1)
    )
    topic_data["currentOxidiserMass"] = data_dict["currentOxidiserMass"]
    data_dict["currentFuelMass"] = data_dict["currentFuelMass"] - (
        massReduced / (CONSTANTS["O2FRatio"] + 1)
    )
    topic_data["currentFuelMass"] = data_dict["currentFuelMass"]
    # TODO: if fuel empty, send "STOP" of timestep = -1 to field, thus stopping analysis
    data_dict["currentRocketTotalMass"] = (
        data_dict["currentRocketTotalMass"] - massReduced
    )
    topic_data["currentRocketTotalMass"] = data_dict["currentRocketTotalMass"]
    logging.debug(f"Timestep: {data_dict['currentTimestep']:5}-{topic_data}")
    send_topic_data(server_socket, "fuel_flow", json.dumps(topic_data))


def run_cycle():
    global cycle_flags
    while True:
        if check_to_run_cycle(cycle_flags):
            make_all_cycle_flags_default(cycle_flags)
            run_one_cycle()


def listen_analysis():
    global data_dict
    global cycle_flags
    logging.info(f"Started Listening for analysis")
    while True:
        topic, info = recv_topic_data(server_socket)
        if topic in cycle_flags.keys():
            cycle_flags[topic] = True
            topic_func_dict[topic](data_dict, info)
        else:
            logging.error(f"{CONFIG_DATA['name']} is not subscribed to {topic}")


# Helper Functions


def listening_function(server_socket):
    global CONFIG_DATA
    global CONSTANTS

    while True:
        try:
            msg = recv_msg(server_socket)
            if msg == "CONFIG":
                send_config(server_socket, CONFIG_DATA)
                CONSTANTS = request_constants(server_socket)
                fill_init_topic_data()
            elif msg == "START":
                analysis_listening_thread = threading.Thread(target=listen_analysis)
                analysis_listening_thread.start()
                break
        except Exception as e:
            logging.error(f"listening_function error: {str(e)}")
            break
    run_cycle()


def main():
    listening_thread = threading.Thread(
        target=listening_function, args=(server_socket,)
    )

    listening_thread.start()


if __name__ == "__main__":
    try:
        main()
    except:
        server_socket.close()
