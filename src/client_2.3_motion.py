import socket
import threading
import json

from client_main.DDS_2.common_functions import (
    check_to_run_cycle,
    drag_received,
    field_received,
    format_msg_with_header,
    fuel_flow_received,
    initialize_cmd_window,
    make_all_cycle_flags_default,
    recv_msg,
    recv_topic_data,
    send_config,
    request_constants,
    send_topic_data,
    thrust_received,
    update_field_topic_date,
    update_motion_topic_data,
)

# Logging
import logging

FORMAT = "%(levelname)-10s %(asctime)s: %(message)s"
# logging.basicConfig(
#     filename="logs_motion.log",
#     encoding="utf-8",
#     level=logging.DEBUG,
#     format=FORMAT,
#     filemode="w",
# )
logging.basicConfig(
    handlers=[
        logging.FileHandler(filename="logs_motion.log", encoding="utf-8", mode="w")
    ],
    level=logging.DEBUG,
    format=FORMAT,
)
# Logging end


HEADERSIZE = 5
CONFIG_DATA = {
    "id": "CLIENT_3",
    "name": "motion",
    "subscribed_topics": [
        "drag",
        "thrust",
        "fuel_flow",
        "field",
        "motion_update_realtime",
    ],
    "published_topics": ["motion"],
    "constants_required": [
        "gravitationalAcceleration",
        "requiredThrust",
        "timestepSize",
        "totalTimesteps",
    ],
    "variables_subscribed": [],
}
initialize_cmd_window(CONFIG_DATA)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind((socket.gethostname(), 55_002))
# server_socket.connect(("192.168.1.2", 1234))
server_socket.connect(("localhost", 1234))

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

all_data_dict = {}

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
    # if data_dict["currentTimestep"] in [60, 105, 185]:
    #     print(f'Reduced at {data_dict["currentTimestep"]=}')
    #     topic_data["currentAltitude"] -= topic_data["currentAltitude"] * 0.05

    all_data_dict[
        f"{data_dict['versions']}.{data_dict['currentTimestep']}"
    ] = topic_data.copy()

    send_topic_data(server_socket, "motion", json.dumps(topic_data))
    logging.info(f"Received {data_dict=}")
    logging.info(f"Timestep: {data_dict['currentTimestep']:5}-{topic_data}")

    if data_dict["currentTimestep"] == 245:
        logging.info(f"\n\n\n{json.dumps(all_data_dict, indent=4)}")


def run_cycle():
    global cycle_flags
    while True:
        if check_to_run_cycle(cycle_flags):
            make_all_cycle_flags_default(cycle_flags)
            run_one_cycle()


# Helper Functions
def listen_analysis():
    global data_dict
    global cycle_flags
    global topic_data

    while True:
        topic, sent_time, recv_time, info = recv_topic_data(server_socket)
        if topic in cycle_flags.keys():
            cycle_flags[topic] = True
            topic_func_dict[topic](data_dict, sent_time, recv_time, info)
        elif topic == "motion_update_realtime":
            # increase version no
            data_dict["versions"] = data_dict["versions"] + 1

            # Make json file
            logging.debug(f"Received Updation : {info=}")
            topic_data_to_update = json.loads(info)
            topic_data_to_update["sent_time_ns"] = sent_time
            topic_data_to_update["recv_time_ns"] = recv_time
            topic_data_to_update["latency"] = recv_time - sent_time

            # add new branch
            all_data_dict[
                f"{data_dict['versions']}.{topic_data_to_update['currentTimestep']}"
            ] = topic_data_to_update

            # Change current topic_data
            update_motion_topic_data(topic_data, topic_data_to_update)

            # Cycle flags to def
            make_all_cycle_flags_default(cycle_flags)

            # send received info as motion topic_data
            send_topic_data(
                server_socket,
                "motion",
                json.dumps(topic_data_to_update),
            )
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
