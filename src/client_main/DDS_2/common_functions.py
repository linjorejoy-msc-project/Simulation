import socket
import math
import json
from typing import Tuple
import time

# Logging
import logging
import os

# file_path = os.path.join(os.path.abspath(os.curdir), "src\\client_main\\LOGS")
# FORMAT = "%(levelname)-10s %(asctime)s: %(name)-25s %(message)s"
# logging.basicConfig(
#     filename=f"logs.log",
#     encoding="utf-8",
#     level=logging.DEBUG,
#     format=FORMAT,
# )
# logger0 = logging.getLogger("common")

# Logging end

HEADERSIZE = 5
TOPICLABELSIZE = 25
TIMEDATASIZE = 20


# Helper Functions
def format_msg_with_header(msg: str, header_size: int = HEADERSIZE):
    return bytes(f"{len(msg):<{header_size}}" + msg, "utf-8")


def format_msg_with_header_and_topic(topic: str, msg: str):
    return format_msg_with_header(f"{topic:25}{msg}")


def recv_msg(server_socket: socket.socket) -> str:
    try:
        while True:
            len_str = server_socket.recv(HEADERSIZE)
            if len_str:
                recv_time = time.perf_counter_ns()
                msg_len = int(len_str)
                return_str = server_socket.recv(msg_len).decode("utf-8")
                if return_str:
                    return return_str
    except Exception as e:
        print(f"Error Occured\n{e}")
        return None


def recv_topic_data(server_socket: socket.socket) -> Tuple[str, int, int, str]:
    msg = recv_msg(server_socket)
    # logging.info(f"Received {msg=}")
    # logging.debug(
    #     f"Check (topic,info) = ({str(msg[:TOPICLABELSIZE]).strip()},{msg[TOPICLABELSIZE:]})"
    # )
    # return_data = (
    #     str(msg[:TOPICLABELSIZE]).strip(),
    #     int(str(msg[TOPICLABELSIZE : TOPICLABELSIZE + TIMEDATASIZE]).strip()),
    #     time.perf_counter_ns(),
    #     msg[TOPICLABELSIZE:],
    # )
    # logging.debug(f"Received {msg=} converted to Tuple {return_data=}")
    return (
        str(msg[:TOPICLABELSIZE]).strip(),
        int(str(msg[TOPICLABELSIZE : TOPICLABELSIZE + TIMEDATASIZE]).strip()),
        int(time.time() * 1000),
        msg[TOPICLABELSIZE + TIMEDATASIZE :],
    )


def send_config(server_socket: socket.socket, config: dict):
    # logging.info(f"Sending config \n{config=}")
    server_socket.send(format_msg_with_header(json.dumps(config)))


def request_constants(server_socket: socket.socket):
    server_socket.send(format_msg_with_header("CONSTANTS"))
    constants_received = recv_msg(server_socket)
    return json.loads(constants_received)

    # print(f"{constants_received=}")


def send_topic_data(server_socket: socket.socket, topic: str, data: str):
    # logging.info(f"{topic=} sending {data=}")
    msgToSend = (
        f"{topic:{TOPICLABELSIZE}}{str(int(time.time()*1000)):{TIMEDATASIZE}}{data}"
    )
    formatted_msg = format_msg_with_header(msgToSend)
    server_socket.send(formatted_msg)
    # logging.debug(
    #     f"{topic=} sending {data=} as format_msg_with_header(msgToSend)= {formatted_msg}"
    # )


def check_to_run_cycle(cycle_flags: dict):
    if cycle_flags:
        return all(cycle_flags.values())
    else:
        return False


def make_all_cycle_flags_default(cycle_flags: dict):
    for key in cycle_flags.keys():
        cycle_flags[key] = False


# Topic specific functions
def field_received(data_dict: dict, sent_time: int, recv_time: int, info: str):
    info_obj = json.loads(info)
    data_dict["currentTimestep"] = info_obj["currentTimestep"]
    data_dict["currentTime"] = info_obj["currentTime"]
    data_dict["totalTimestepsRun"] = info_obj["totalTimestepsRun"]
    data_dict["versions"] = info_obj["versions"]
    data_dict["sent_time_ns"] = sent_time
    data_dict["recv_time_ns"] = recv_time
    data_dict["latency_ms"] = recv_time - sent_time


def fuel_flow_received(data_dict: dict, sent_time: int, recv_time: int, info: str):
    info_obj = json.loads(info)
    data_dict["currentMassFlowRate"] = info_obj["currentMassFlowRate"]
    data_dict["currentOxidiserMass"] = info_obj["currentOxidiserMass"]
    data_dict["currentFuelMass"] = info_obj["currentFuelMass"]
    data_dict["currentRocketTotalMass"] = info_obj["currentRocketTotalMass"]
    data_dict["sent_time_ns"] = sent_time
    data_dict["recv_time_ns"] = recv_time
    data_dict["latency_ms"] = recv_time - sent_time


def thrust_received(data_dict: dict, sent_time: int, recv_time: int, info: str):
    info_obj = json.loads(info)
    data_dict["currentThrust"] = info_obj["currentThrust"]
    data_dict["sent_time_ns"] = sent_time
    data_dict["recv_time_ns"] = recv_time
    data_dict["latency_ms"] = recv_time - sent_time


def drag_received(data_dict: dict, sent_time: int, recv_time: int, info: str):
    info_obj = json.loads(info)
    data_dict["drag"] = info_obj["drag"]
    data_dict["sent_time_ns"] = sent_time
    data_dict["recv_time_ns"] = recv_time
    data_dict["latency_ms"] = recv_time - sent_time


def motion_received(data_dict: dict, sent_time: int, recv_time: int, info: str):
    info_obj = json.loads(info)
    data_dict["netThrust"] = info_obj["netThrust"]
    data_dict["currentAcceleration"] = info_obj["currentAcceleration"]
    data_dict["currentVelocityDelta"] = info_obj["currentVelocityDelta"]
    data_dict["currentVelocity"] = info_obj["currentVelocity"]
    data_dict["currentAltitudeDelta"] = info_obj["currentAltitudeDelta"]
    data_dict["currentAltitude"] = info_obj["currentAltitude"]
    data_dict["requiredThrustChange"] = info_obj["requiredThrustChange"]
    data_dict["sent_time_ns"] = sent_time
    data_dict["recv_time_ns"] = recv_time
    data_dict["latency_ms"] = recv_time - sent_time


def atmosphere_received(data_dict: dict, sent_time: int, recv_time: int, info: str):
    info_obj = json.loads(info)
    data_dict["pressure"] = info_obj["pressure"]
    data_dict["temperature"] = info_obj["temperature"]
    data_dict["density"] = info_obj["density"]
    data_dict["sent_time_ns"] = sent_time
    data_dict["recv_time_ns"] = recv_time
    data_dict["latency_ms"] = recv_time - sent_time


def process_topic_field_update(data: str, sent_time: int, recv_time: int, variables):

    try:
        dataObj: dict = json.loads(data)
        for key in dataObj.keys():
            variables[key] = dataObj[key]
        variables["sent_time_ns"] = sent_time
        variables["recv_time_ns"] = recv_time
        variables["latency"] = recv_time - sent_time
        if dataObj["currentTimestep"] == -1:
            return False
        else:
            return True

    except Exception as e:
        logging.error(e)
    return False


def generate_field_update_data(response_dict):
    return_dict = {}
    return_dict["currentTimestep"] = response_dict["currentTimestep"]
    return_dict["currentTime"] = response_dict["currentTime"]
    return_dict["versions"] = response_dict["versions"]
    return json.dumps(return_dict)


def update_field_topic_date(topic_data, updated_dict):
    topic_data["currentTimestep"] = updated_dict["currentTimestep"]
    topic_data["currentTime"] = updated_dict["currentTime"]
    topic_data["versions"] = updated_dict["versions"]


def generate_motion_update_data(response_dict):
    return_dict = {}
    return_dict["currentTimestep"] = response_dict["currentTimestep"]
    return_dict["netThrust"] = response_dict["netThrust"]
    return_dict["currentAcceleration"] = response_dict["currentAcceleration"]
    return_dict["currentVelocityDelta"] = response_dict["currentVelocityDelta"]
    return_dict["currentVelocity"] = response_dict["currentVelocity"]
    return_dict["currentAltitudeDelta"] = response_dict["currentAltitudeDelta"]
    return_dict["currentAltitude"] = response_dict["currentAltitude"]
    return_dict["requiredThrustChange"] = response_dict["requiredThrustChange"]
    return json.dumps(return_dict)


def update_motion_topic_data(topic_data, updated_dict):
    topic_data["currentTimestep"] = updated_dict["currentTimestep"]
    topic_data["netThrust"] = updated_dict["netThrust"]
    topic_data["currentAcceleration"] = updated_dict["currentAcceleration"]
    topic_data["currentVelocityDelta"] = updated_dict["currentVelocityDelta"]
    topic_data["currentVelocity"] = updated_dict["currentVelocity"]
    topic_data["currentAltitudeDelta"] = updated_dict["currentAltitudeDelta"]
    topic_data["currentAltitude"] = updated_dict["currentAltitude"]
    topic_data["requiredThrustChange"] = updated_dict["requiredThrustChange"]


def generate_fuel_flow_update_data(response_dict):
    return_dict = {}
    return_dict["currentTimestep"] = response_dict["currentTimestep"]
    return_dict["currentMassFlowRate"] = response_dict["currentMassFlowRate"]
    return_dict["currentOxidiserMass"] = response_dict["currentOxidiserMass"]
    return_dict["currentFuelMass"] = response_dict["currentFuelMass"]
    return_dict["currentRocketTotalMass"] = response_dict["currentRocketTotalMass"]
    return json.dumps(return_dict)


def update_fuel_flow_topic_data(topic_data, updated_dict):
    topic_data["currentTimestep"] = updated_dict["currentTimestep"]
    topic_data["currentMassFlowRate"] = updated_dict["currentMassFlowRate"]
    topic_data["currentOxidiserMass"] = updated_dict["currentOxidiserMass"]
    topic_data["currentFuelMass"] = updated_dict["currentFuelMass"]
    topic_data["currentRocketTotalMass"] = updated_dict["currentRocketTotalMass"]


# Calculation Functions
def external_pressure_temperature(altitude: float):
    T = 0.0
    P = 0.0
    if altitude < 11000:
        T = 15.04 - 0.00649 * altitude
        P = 101.29 * ((T + 273.1) / 288.08) ** 5.256
    elif altitude >= 11000 and altitude < 25000:
        T = -56.46
        P = 22.65 * math.exp(1.73 - 0.000157 * altitude)
    else:
        T = -131.21 + 0.00299 * altitude
        P = 2.488 * ((T + 273.1) / 216.6) ** -11.388
    return P, T


def get_air_density(altitude: float = 0, pressure=0, temperature=0):
    if pressure and temperature:
        return pressure / (0.2869 * (temperature + 273.1))
    P, T = external_pressure_temperature(altitude)
    return P / (0.2869 * (T + 273.1))


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


def initialize_cmd_window(CONFIGDATA: dict):

    width = 50
    fill_char = "."

    # Print name
    print(fill_char * width)
    print(f" {CONFIGDATA['name']} ".center(width, fill_char))
    print(fill_char * width)

    # Print id
    print(f"{CONFIGDATA['id']} ".ljust(width, fill_char))
    print(fill_char * width)
    print(fill_char * width)
    print(fill_char * width)

    # Subscribed topics
    print("SUBSCRIBED TOPICS".center(width, fill_char))
    for i, topic in enumerate(CONFIGDATA["subscribed_topics"]):
        print(f"{i+1}. {topic}".ljust(width, fill_char))
    print(fill_char * width)
    print(fill_char * width)

    # Published topics
    print("PUBLISHED TOPICS".center(width, fill_char))
    for i, topic in enumerate(CONFIGDATA["published_topics"]):
        print(f"{i+1}. {topic}".ljust(width, fill_char))
    print(fill_char * width)
    print(fill_char * width)


if __name__ == "__main__":
    initialize_cmd_window(CONFIG_DATA)
