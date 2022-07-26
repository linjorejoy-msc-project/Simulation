import socket
import math
import json
from typing import Tuple

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
                msg_len = int(len_str)
                return_str = server_socket.recv(msg_len).decode("utf-8")
                if return_str:
                    return return_str
    except Exception as e:
        print(f"Error Occured\n{e}")
        return None


def recv_topic_data(server_socket: socket.socket) -> Tuple[str, str]:
    msg = recv_msg(server_socket)
    # logging.info(f"Received {msg=}")
    # logging.debug(
    #     f"Check (topic,info) = ({str(msg[:TOPICLABELSIZE]).strip()},{msg[TOPICLABELSIZE:]})"
    # )
    return str(msg[:TOPICLABELSIZE]).strip(), msg[TOPICLABELSIZE:]


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
    msgToSend = f"{topic:25}{data}"
    server_socket.send(format_msg_with_header(msgToSend))
    logging.info(f"{topic=} sending {data=} as {format_msg_with_header(msgToSend)=}")


def check_to_run_cycle(cycle_flags: dict):
    return all(cycle_flags.values())


def make_all_cycle_flags_default(cycle_flags: dict):
    for key in cycle_flags.keys():
        cycle_flags[key] = False


# Topic specific functions
def field_received(data_dict: dict, info: str):
    info_obj = json.loads(info)
    data_dict["currentTimestep"] = info_obj["currentTimestep"]


def fuel_flow_received(data_dict: dict, info: str):
    info_obj = json.loads(info)
    data_dict["currentMassFlowRate"] = info_obj["currentMassFlowRate"]
    data_dict["currentOxidiserMass"] = info_obj["currentOxidiserMass"]
    data_dict["currentFuelMass"] = info_obj["currentFuelMass"]
    data_dict["currentRocketTotalMass"] = info_obj["currentRocketTotalMass"]


def thrust_received(data_dict: dict, info: str):
    info_obj = json.loads(info)
    data_dict["currentThrust"] = info_obj["currentThrust"]


def drag_received(data_dict: dict, info: str):
    info_obj = json.loads(info)
    data_dict["drag"] = info_obj["drag"]


def motion_received(data_dict: dict, info: str):
    info_obj = json.loads(info)
    data_dict["netThrust"] = info_obj["netThrust"]
    data_dict["currentAcceleration"] = info_obj["currentAcceleration"]
    data_dict["currentVelocityDelta"] = info_obj["currentVelocityDelta"]
    data_dict["currentVelocity"] = info_obj["currentVelocity"]
    data_dict["currentAltitudeDelta"] = info_obj["currentAltitudeDelta"]
    data_dict["currentAltitude"] = info_obj["currentAltitude"]
    data_dict["requiredThrustChange"] = info_obj["requiredThrustChange"]


def atmosphere_received(data_dict: dict, info: str):
    info_obj = json.loads(info)
    data_dict["pressure"] = info_obj["pressure"]
    data_dict["temperature"] = info_obj["temperature"]
    data_dict["density"] = info_obj["density"]


def process_topic_field_update(data: str, variables):

    try:
        dataObj: dict = json.loads(data)
        for key in dataObj.keys():
            variables[key] = dataObj[key]
        if dataObj["currentTimestep"] == -1:
            return False
        else:
            return True

    except Exception as e:
        logging.error(e)
    return False


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
