import socket
import threading
import json

from client_main.DDS_2.common_functions import (
    check_to_run_cycle,
    format_msg_with_header,
    format_msg_with_header_and_topic,
    make_all_cycle_flags_default,
    recv_msg,
    recv_topic_data,
    send_config,
    request_constants,
    field_received,
    fuel_flow_received,
    send_topic_data,
)

# Logging
import logging
import os

file_path = os.path.join(os.path.abspath(os.curdir), "src\\client_main\\LOGS")

FORMAT = "%(levelname)-10s %(asctime)s: %(message)s"
logging.basicConfig(
    filename="logs_engine.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format=FORMAT,
    filemode="w",
)

# Logging end


HEADERSIZE = 5
CONFIG_DATA = {
    "id": "CLIENT_2",
    "name": "engine",
    "subscribed_topics": ["fuel_flow", "field"],
    "published_topics": ["thrust"],
    "constants_required": [
        "requiredThrust",
        "specificImpulse",
        "gravitationalAcceleration",
        "timestepSize",
        "totalTimesteps",
    ],
    "variables_subscribed": [],
}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect((socket.gethostname(), 1234))

CONSTANTS = {}

topic_data = {"currentThrust": 0}

cycle_flags = {"fuel_flow": False, "field": False}

# topic specific functions
topic_func_dict = {"fuel_flow": fuel_flow_received, "field": field_received}

# to store data received
data_dict = {}

# Helper Functions
def fill_init_topic_data():
    global topic_data
    topic_data["currentThrust"] = CONSTANTS["requiredThrust"]


def start_initiation():
    global topic_data
    send_topic_data(server_socket, "thrust", json.dumps(topic_data))


def run_one_cycle():
    # Run one simulation
    global server_socket
    topic_data["currentThrust"] = (
        CONSTANTS["specificImpulse"]
        * CONSTANTS["gravitationalAcceleration"]
        * data_dict["currentMassFlowRate"]
    )
    # send_topic_data after dumping to string
    logging.info(f"{topic_data=}")
    send_topic_data(server_socket, "thrust", json.dumps(topic_data))


def listen_analysis():
    global data_dict
    global cycle_flags
    while True:
        topic, info = recv_topic_data(server_socket)
        if topic in cycle_flags.keys():
            cycle_flags[topic] = True
            topic_func_dict[topic](data_dict, info)
        else:
            print(f"{CONFIG_DATA['name']} is not subscribed to {topic}")
        if check_to_run_cycle(cycle_flags):
            # Run a cycle
            cycle_thread = threading.Thread(target=run_one_cycle)
            cycle_thread.start()
            make_all_cycle_flags_default(cycle_flags)


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
                analysis_thread = threading.Thread(target=start_initiation)
                analysis_listening_thread = threading.Thread(target=listen_analysis)
                analysis_thread.start()
                analysis_listening_thread.start()
                break
        except Exception as e:
            print(f"Error Occured\n{e}")
            break


def main():
    listening_thread = threading.Thread(
        target=listening_function, args=(server_socket,)
    )
    # sending_thread = threading.Thread()
    # analysis_thread = threading.Thread()

    listening_thread.start()
    # sending_thread.start()
    # analysis_thread.start()


if __name__ == "__main__":
    main()