import socket
import threading
import json

from client_main.DDS_2.common_functions import (
    atmosphere_received,
    check_to_run_cycle,
    field_received,
    format_msg_with_header,
    get_air_density,
    initialize_cmd_window,
    make_all_cycle_flags_default,
    motion_received,
    recv_msg,
    recv_topic_data,
    send_config,
    request_constants,
    send_topic_data,
)

# Logging
import logging

FORMAT = "%(levelname)-10s %(asctime)s: %(message)s"
# logging.basicConfig(
#     filename="logs_aerodynamics.log",
#     encoding="utf-8",
#     level=logging.DEBUG,
#     format=FORMAT,
#     filemode="w",
# )
logging.basicConfig(
    handlers=[
        logging.FileHandler(
            filename="logs_aerodynamics.log", encoding="utf-8", mode="w"
        )
    ],
    level=logging.DEBUG,
    format=FORMAT,
)
# Logging end


HEADERSIZE = 5
CONFIG_DATA = {
    "id": "CLIENT_4",
    "name": "aerodynamics",
    "subscribed_topics": ["motion", "atmosphere", "field"],
    "published_topics": ["drag", "field_update"],
    "constants_required": [
        "dragCoefficient",
        "rocketFrontalArea",
        "timestepSize",
        "totalTimesteps",
    ],
    "variables_subscribed": [],
}
initialize_cmd_window(CONFIG_DATA)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind((socket.gethostname(), 55_003))
# server_socket.connect(("192.168.1.2", 1234))
server_socket.connect(("localhost", 1234))

CONSTANTS = {}

topic_data = {"drag": 0}

cycle_flags = {"motion": False, "atmosphere": False, "field": False}

topic_func_dict = {
    "motion": motion_received,
    "atmosphere": atmosphere_received,
    "field": field_received,
}

data_dict = {}
# Helper Functions


def fill_init_topic_data():
    pass


def run_one_cycle():
    topic_data["drag"] = (
        CONSTANTS["dragCoefficient"]
        * data_dict["density"]
        * data_dict["currentVelocity"]
        * data_dict["currentVelocity"]
        * CONSTANTS["rocketFrontalArea"]
        / 2
    )
    logging.info(f"Received {data_dict=}")
    send_topic_data(server_socket, "drag", json.dumps(topic_data))
    send_topic_data(
        server_socket,
        "field_update",
        json.dumps(
            {
                "currentTimestep": data_dict["currentTimestep"] + 1,
                "currentTime": CONSTANTS["timestepSize"]
                * (data_dict["currentTimestep"] + 1),
                "totalTimestepsRun": data_dict["totalTimestepsRun"] + 1,
                "versions": data_dict["versions"],
            }
        ),
    )
    logging.info(f"Timestep: {data_dict['currentTimestep']:5}-{topic_data}")


def run_cycle():
    global cycle_flags
    while True:
        if check_to_run_cycle(cycle_flags):
            make_all_cycle_flags_default(cycle_flags)
            run_one_cycle()


def start_initiation():
    global topic_data
    send_topic_data(server_socket, "drag", json.dumps(topic_data))
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
