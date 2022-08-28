import socket
import threading
import json

from client_main.DDS_2.common_functions import (
    check_to_run_cycle,
    format_msg_with_header,
    format_msg_with_header_and_topic,
    initialize_cmd_window,
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
# logging.basicConfig(
#     filename="logs_engine.log",
#     encoding="utf-8",
#     level=logging.DEBUG,
#     format=FORMAT,
#     filemode="w",
# )
logging.basicConfig(
    handlers=[
        logging.FileHandler(filename="logs_engine.log", encoding="utf-8", mode="w")
    ],
    level=logging.DEBUG,
    format=FORMAT,
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
initialize_cmd_window(CONFIG_DATA)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind((socket.gethostname(), 55_001))
# server_socket.connect(("192.168.1.2", 1234))
server_socket.connect(("localhost", 1234))

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


def run_one_cycle():
    # Run one simulation
    global server_socket
    global data_dict

    topic_data["currentThrust"] = (
        CONSTANTS["specificImpulse"]
        * CONSTANTS["gravitationalAcceleration"]
        * data_dict["currentMassFlowRate"]
    )
    logging.info(f"Received {data_dict=}")
    logging.info(f"Timestep: {data_dict['currentTimestep']:5}-{topic_data}")
    send_topic_data(server_socket, "thrust", json.dumps(topic_data))


def run_cycle():
    global cycle_flags
    while True:
        if check_to_run_cycle(cycle_flags):
            make_all_cycle_flags_default(cycle_flags)
            run_one_cycle()


def start_initiation():
    global topic_data
    send_topic_data(server_socket, "thrust", json.dumps(topic_data))
    run_cycle()


def listen_analysis():
    global data_dict
    global cycle_flags
    while True:
        topic, sent_time, recv_time, info = recv_topic_data(server_socket)
        if topic in cycle_flags.keys():
            cycle_flags[topic] = True
            topic_func_dict[topic](data_dict, sent_time, recv_time, info)
        else:
            print(f"{CONFIG_DATA['name']} is not subscribed to {topic}")


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
            print(f"Error Occured\n{e}")
            break
    start_initiation()


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
