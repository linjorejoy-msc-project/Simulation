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
    recv_msg,
    recv_topic_data,
    send_config,
    request_constants,
    send_topic_data,
    thrust_received,
)

# Logging
import logging

FORMAT = "%(levelname)-10s %(asctime)s: %(message)s"
logging.basicConfig(
    filename="logs_motion.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format=FORMAT,
    filemode="w",
)

# Logging end


HEADERSIZE = 5
CONFIG_DATA = {
    "id": "CLIENT_3",
    "name": "motion",
    "subscribed_topics": ["drag", "thrust", "fuel_flow", "field"],
    "published_topics": ["motion"],
    "constants_required": [
        "gravitationalAcceleration",
        "requiredThrust",
        "timestepSize",
        "totalTimesteps",
    ],
    "variables_subscribed": [],
}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect((socket.gethostname(), 1234))

CONSTANTS = {}

topic_data = {
    "netThrust": 0,
    "currentAcceleration": 0,
    "currentVelocityDelta": 0,
    "currentVelocity": 0,
    "currentAltitudeDelta": 0,
    "currentAltitude": 0,
    "requiredThrustChange": 0,
}

data_dict = {}

cycle_flags = {"drag": False, "thrust": False, "fuel_flow": False, "field": False}
topic_func_dict = {
    "drag": drag_received,
    "thrust": thrust_received,
    "fuel_flow": fuel_flow_received,
    "field": field_received,
}


def fill_init_topic_data():
    global topic_data
    topic_data["currentAcceleration"] = 0
    topic_data["currentVelocity"] = 0
    topic_data["currentAltitude"] = 0


def run_one_cycle():
    topic_data["netThrust"] = (
        CONSTANTS["requiredThrust"]
        - data_dict["currentRocketTotalMass"] * CONSTANTS["gravitationalAcceleration"]
        - data_dict["drag"]
    )
    topic_data["requiredThrustChange"] = (
        (CONSTANTS["requiredThrust"] - topic_data["netThrust"])
        * 100
        / CONSTANTS["requiredThrust"]
    )
    topic_data["currentAcceleration"] = (
        topic_data["netThrust"] / data_dict["currentRocketTotalMass"]
    )
    topic_data["currentVelocityDelta"] = (
        topic_data["currentAcceleration"] * CONSTANTS["timestepSize"]
    )
    topic_data["currentVelocity"] = (
        topic_data["currentVelocity"] + topic_data["currentVelocityDelta"]
    )
    topic_data["currentAltitudeDelta"] = (
        topic_data["currentVelocity"] * CONSTANTS["timestepSize"]
    )
    topic_data["currentAltitude"] = (
        topic_data["currentAltitude"] + topic_data["currentAltitudeDelta"]
    )
    send_topic_data(server_socket, "motion", json.dumps(topic_data))
    logging.debug(f"Timestep: {data_dict['currentTimestep']:5}-{topic_data}")


def run_cycle():
    global cycle_flags
    while True:
        if check_to_run_cycle(cycle_flags):
            run_one_cycle()
            make_all_cycle_flags_default(cycle_flags)


# Helper Functions
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
                analysis_thread = threading.Thread(target=run_cycle)
                analysis_listening_thread.start()
                analysis_thread.start()
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
    try:
        main()
    except:
        server_socket.close()
