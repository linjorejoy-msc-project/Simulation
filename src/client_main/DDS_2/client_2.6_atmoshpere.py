import socket
import threading
import json


# Logging
import logging

from client_main.DDS_2.common_functions import (
    check_to_run_cycle,
    external_pressure_temperature,
    field_received,
    get_air_density,
    make_all_cycle_flags_default,
    motion_received,
    recv_msg,
    recv_topic_data,
    request_constants,
    send_config,
    send_topic_data,
)

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
        logging.FileHandler(filename="logs_atmosphere.log", encoding="utf-8", mode="w")
    ],
    level=logging.DEBUG,
    format=FORMAT,
)

# Logging end


HEADERSIZE = 5
CONFIG_DATA = {
    "id": "CLIENT_4",
    "name": "aerodynamics",
    "subscribed_topics": ["motion", "field"],
    "published_topics": ["atmosphere"],
    "constants_required": [
        "timestepSize",
        "totalTimesteps",
    ],
    "variables_subscribed": [],
}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind((socket.gethostname(), 55_005))
server_socket.connect(("192.168.1.4", 1234))

CONSTANTS = {}

topic_data = {"pressure": 0, "temperature": 0, "density": 0}

cycle_flags = {"motion": False, "field": False}

topic_func_dict = {"motion": motion_received, "field": field_received}

data_dict = {}
# Helper Functions


def fill_init_topic_data():

    topic_data["pressure"], topic_data["temperature"] = external_pressure_temperature(0)
    topic_data["density"] = get_air_density(
        pressure=topic_data["pressure"], temperature=topic_data["temperature"]
    )


def run_one_cycle():

    topic_data["pressure"], topic_data["temperature"] = external_pressure_temperature(
        data_dict["currentAltitude"]
    )
    topic_data["density"] = get_air_density(
        pressure=topic_data["pressure"], temperature=topic_data["temperature"]
    )
    send_topic_data(server_socket, "atmosphere", json.dumps(topic_data))
    logging.debug(f"Timestep: {data_dict['currentTimestep']:5}-{topic_data}")


def run_cycle():
    global cycle_flags
    while True:
        if check_to_run_cycle(cycle_flags):
            make_all_cycle_flags_default(cycle_flags)
            run_one_cycle()


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
            print(f"Error Occured\n{e}")
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
