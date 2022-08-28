import socket
import threading
import requests
import time

from client_main.DDS_2.common_functions import (
    check_to_run_cycle,
    drag_received,
    field_received,
    format_msg_with_header,
    fuel_flow_received,
    generate_field_update_data,
    generate_fuel_flow_update_data,
    generate_motion_update_data,
    initialize_cmd_window,
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
            filename="logs_real_time_updater.log", encoding="utf-8", mode="w"
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
    "subscribed_topics": [],
    "published_topics": [
        "field_update_realtime",
        "motion_update_realtime",
        "fuel_flow_update_realtime",
    ],
    "constants_required": [],
    "variables_subscribed": [],
}
initialize_cmd_window(CONFIG_DATA)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect(("localhost", 1234))

API_BASE_URL = "http://127.0.0.1:7777"
api_routes = {
    1: "/",
    2: "/real/",
    3: "/altered1/",
    4: "/altered2/",
    5: "/altered3/",
    6: "/altered4/",
    7: "/data/",
}
global param
param = {"timestart": int(time.time())}

API_ROUTE_SELECTED = f"{API_BASE_URL}{api_routes[7]}"

CONSTANTS = {}

cycle_flags = {}
topic_func_dict = {}

# to store data received
data_dict = {}

global current_response
current_response = {"currentTimestep": 0}

# Actual Analysis
# def run_one_cycle():
#     global data_dict
#     logging.debug(f"Timestep: {data_dict['currentTimestep']:5}-{data_dict}")


# def run_cycle():
#     global cycle_flags
#     while True:
#         if check_to_run_cycle(cycle_flags):
#             make_all_cycle_flags_default(cycle_flags)
#             run_one_cycle()


def listen_analysis():
    global data_dict
    global cycle_flags
    global param

    logging.info(f"Started Listening for analysis")

    param = {"timestart": int(time.time())}
    while True:
        topic, sent_time, recv_time, info = recv_topic_data(server_socket)
        if cycle_flags:
            if topic in cycle_flags.keys():
                cycle_flags[topic] = True
                topic_func_dict[topic](data_dict, sent_time, recv_time, info)
            else:
                logging.error(f"{CONFIG_DATA['name']} is not subscribed to {topic}")


def api_listener():
    global current_response
    global param

    while True:
        # try:
        time.sleep(1)
        response_json = requests.get(API_ROUTE_SELECTED, params=param).json()
        received_data = response_json["data"]
        if received_data["currentTimestep"] is not current_response["currentTimestep"]:
            current_response = received_data
            send_topic_data(
                server_socket,
                "field_update_realtime",
                generate_field_update_data(current_response),
            )
            send_topic_data(
                server_socket,
                "motion_update_realtime",
                generate_motion_update_data(current_response),
            )
            send_topic_data(
                server_socket,
                "fuel_flow_update_realtime",
                generate_fuel_flow_update_data(current_response),
            )
            logging.debug(
                f"Timestep: {current_response['currentTimestep']:5}-{current_response}"
            )
    # except:
    #     print("Error Occured while connecting to api")


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
    api_listener()


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
