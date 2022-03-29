import math
import socket
import threading
import json


HEADERSIZE = 5
CONFIG_DATA = {
    "id": "CLIENT_5",
    "name": "fields",
    "subscribed_topics": ["field"],
    "published_topics": ["field"],
    "constants_required": [],
    "variables_subscribed": [],
}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect((socket.gethostname(), 1234))

CONSTANTS = {
    "timestepSize": 1,
    "totalTimesteps": 500,
    "requiredThrust": 123_191_000.0,
    "initialDrag": 0,
    "dragCoefficient": 0.75,
    "rocketTotalMass": 7_982_000,
    "rocketUnfuelledMass": 431_000,
    "initialRocketOFMass": 0,
    "O2FRatio": 6,
    "initialOxidiserMass": 0,
    "initialFuelMass": 0,
    "rocketBodyDiameter": 21.3,
    "rocketFrontalArea": 0,
    "specificImpulse": 410,
    "gravitationalAcceleration": 9.81,
    "initialRequiredMassFlowRate": 0,
}


class FieldTopic:
    def __init__(self) -> None:
        self.current_timestep
        self.current_time

    def to_dict(self, obj):
        return json.dumps(obj, default=lambda o: o.__dict__, indent=2)


def calculate_constants():
    CONSTANTS["initialRocketOFMass"] = (
        CONSTANTS["rocketTotalMass"] - CONSTANTS["rocketUnfuelledMass"]
    )
    CONSTANTS["initialOxidiserMass"] = (
        CONSTANTS["O2FRatio"]
        * CONSTANTS["initialRocketOFMass"]
        / (CONSTANTS["O2FRatio"] + 1)
    )
    CONSTANTS["initialFuelMass"] = CONSTANTS["initialRocketOFMass"] / (
        CONSTANTS["O2FRatio"] + 1
    )
    CONSTANTS["rocketFrontalArea"] = (
        math.pi * CONSTANTS["rocketBodyDiameter"] * CONSTANTS["rocketBodyDiameter"]
    )
    CONSTANTS["initialRequiredMassFlowRate"] = CONSTANTS["requiredThrust"] / (
        CONSTANTS["specificImpulse"] * CONSTANTS["gravitationalAcceleration"]
    )


def subscribed_data_receive(msg: str):
    pass


# Helper Functions
def format_msg_with_header(msg: str, header_size: int = HEADERSIZE):
    return bytes(f"{len(msg):<{header_size}}" + msg, "utf-8")


def recv_msg(server_socket: socket.socket) -> str:
    try:
        msg_len = int(server_socket.recv(HEADERSIZE))
        return server_socket.recv(msg_len).decode("utf-8")
    except Exception as e:
        print(f"Error Occured\n{e}")
        return None


def send_config(server_socket: socket.socket):
    global CONFIG_DATA

    data = json.dumps(CONFIG_DATA)
    server_socket.send(format_msg_with_header(json.dumps(CONFIG_DATA)))


def send_constants(server_socket: socket.socket):
    server_socket.send(format_msg_with_header(json.dumps(CONSTANTS)))


def request_constants(server_socket: socket.socket):
    server_socket.send(format_msg_with_header("CONSTANTS"))
    constants_received = recv_msg(server_socket)
    print(f"{constants_received=}")


def listening_function(server_socket):
    while True:
        try:
            msg = recv_msg(server_socket)
            if msg == "CONFIG":
                send_config(server_socket)
                # request_constants(server_socket)
            elif msg == "CONSTANTS":
                send_constants(server_socket)
            else:
                subscribed_data_receive(msg)
                print(f"subscribed_data_receive called")
                break
        except Exception as e:
            print(f"Error Occured\n{e}")
            break


def main():
    calculate_constants()
    listening_thread = threading.Thread(
        target=listening_function, args=(server_socket,)
    )
    # sending_thread = threading.Thread()
    # analysis_thread = threading.Thread()

    listening_thread.start()
    # sending_thread.start()
    # analysis_thread.start()


if __name__ == "__main__":
    main()
