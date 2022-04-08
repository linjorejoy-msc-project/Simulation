import socket
import threading
import json

from client_main.DDS_2.common_functions import (
    check_to_run_cycle,
    field_received,
    format_msg_with_header,
    get_air_density,
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
logging.basicConfig(
    filename="logs_aerodynamics.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format=FORMAT,
    filemode="w",
)

# Logging end


HEADERSIZE = 5
CONFIG_DATA = {
    "id": "CLIENT_4",
    "name": "aerodynamics",
    "subscribed_topics": ["motion", "field"],
    "published_topics": ["drag", "field_update"],
    "constants_required": [
        "dragCoefficient",
        "rocketFrontalArea",
        "timestepSize",
        "totalTimesteps",
    ],
    "variables_subscribed": [],
}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect((socket.gethostname(), 1234))

CONSTANTS = {}

topic_data = {"drag": 0}

cycle_flags = {"motion": False, "field": False}

topic_func_dict = {"motion": motion_received, "field": field_received}

data_dict = {}
# Helper Functions


def fill_init_topic_data():
    pass


def run_one_cycle():
    topic_data["drag"] = (
        CONSTANTS["dragCoefficient"]
        * get_air_density(data_dict["currentAltitude"])
        * data_dict["currentVelocity"]
        * data_dict["currentVelocity"]
        * CONSTANTS["rocketFrontalArea"]
        / 2
    )
    send_topic_data(server_socket, "drag", json.dumps(topic_data))
    send_topic_data(
        server_socket,
        "field_update",
        json.dumps({"currentTimestep": data_dict["currentTimestep"] + 1}),
    )
    logging.debug(f"Timestep: {data_dict['currentTimestep']:5}-{topic_data}")


def run_cycle():
    global cycle_flags
    while True:
        if check_to_run_cycle(cycle_flags):
            run_one_cycle()
            make_all_cycle_flags_default(cycle_flags)


def start_initiation():
    global topic_data
    send_topic_data(server_socket, "drag", json.dumps(topic_data))
    run_cycle()


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
        # if check_to_run_cycle(cycle_flags):
        #     # Run a cycle
        #     cycle_thread = threading.Thread(target=run_one_cycle)
        #     cycle_thread.start()
        #     make_all_cycle_flags_default(cycle_flags)


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
                # analysis_thread = threading.Thread(target=start_initiation)
                analysis_listening_thread.start()
                # analysis_thread.start()
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
