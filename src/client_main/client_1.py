import socket
import json

from client_main.logger import add_log, write_log

# from logger import add_log, write_log
from socket_test.client import HEADERSIZE

HEADERSIZE = 8
CONFIG_DATA = {
    "id": "CLIENT_1",
    "name": "fuel_tank",
    "subscribed_topics": ["fuel_flow"],
    "published_topics": ["thrust_change"],
    "constants_required": ["specificImpulse"],
    "variables_subscribed": [
        "currentThrust",
        "currentMassFlowRate",
        "currentOxidiserMass",
        "currentFuelMass",
        "currentRocketTotalMass",
    ],
}


def connect_to_server(
    addressFamily=socket.AF_INET,
    socketKind=socket.SOCK_STREAM,
    hostName=socket.gethostname(),
    port: int = 1234,
):
    add_log(
        "INFO",
        f"Attempting to Connect to server in {socketKind} in host {hostName} at port {port}",
    )
    # server_socket = socket.socket(addressFamily, socketKind)
    # server_socket.connect((hostName, port))
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((socket.gethostname(), 1234))
    add_log(
        "INFO", f"Server in {socketKind} in host {hostName} at port {port} is started"
    )
    return server_socket


def send_data_to_server(server_socket, data):
    data = f"{len(data):<{HEADERSIZE}}" + data
    print(f"Data Sent : {data=}")
    server_socket.send(bytes(data, "utf-8"))


def send_config_data(server_socket):
    global CONFIG_DATA
    data = json.dumps(CONFIG_DATA)
    send_data_to_server(server_socket=server_socket, data=data)


def main():
    server_socket = connect_to_server()
    send_config_data(server_socket)
    # send_config_data("server_socket")


if __name__ == "__main__":
    # main()
    try:
        main()
    except ConnectionResetError:
        add_log("ERROR", "Connection Reset Error")
    except:
        add_log("ERROR", "Error Occured")
    finally:
        write_log()
