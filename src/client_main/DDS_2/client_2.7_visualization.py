import math
import socket
import threading
import json

from client_main.DDS_2.common_functions import (
    check_to_run_cycle,
    drag_received,
    field_received,
    format_msg_with_header,
    fuel_flow_received,
    make_all_cycle_flags_default,
    motion_received,
    recv_msg,
    recv_topic_data,
    request_constants,
    send_config,
    send_topic_data,
    thrust_received,
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
        logging.FileHandler(
            filename="logs_visualization.log", encoding="utf-8", mode="w"
        )
    ],
    level=logging.DEBUG,
    format=FORMAT,
)
# Logging end

HEADERSIZE = 5
CONFIG_DATA = {
    "id": "CLIENT_7",
    "name": "visualization",
    "subscribed_topics": [
        "motion",
        "field",
        "thrust",
        "fuel_flow",
        "drag",
    ],
    "published_topics": [],
    "constants_required": [],
    "variables_subscribed": [],
}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect(("localhost", 1234))

CONSTANTS = {}

cycle_flags = {
    "motion": False,
    "field": False,
    "thrust": False,
    "fuel_flow": False,
    "drag": False,
}
topic_func_dict = {
    "motion": motion_received,
    "field": field_received,
    "thrust": thrust_received,
    "fuel_flow": fuel_flow_received,
    "drag": drag_received,
}

# to store data received
data_dict = {}


# Actual Analysis
def run_one_cycle():
    global data_dict
    logging.debug(f"Timestep: {data_dict['currentTimestep']:5}-{data_dict}")


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
