import socket
import threading
import json



# Logging
import logging

from client_main.DDS_2.common_functions import field_received, motion_received

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