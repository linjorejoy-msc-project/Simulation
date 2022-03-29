import socket

import json

import threading
import time

# from logger import add_log, write_log

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect((socket.gethostname(), 1234))

HEADERSIZE = 5
server_config = {}
server_config_received = True
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


# def connect_to_server(
#     addressFamily=socket.AF_INET,
#     socketKind=socket.SOCK_STREAM,
#     hostName=socket.gethostname(),
#     port: int = 1234,
# ):
#     add_log(
#         "INFO",
#         f"Attempting to Connect to server in {socketKind} in host {hostName} at port {port}",
#     )
#     # server_socket = socket.socket(addressFamily, socketKind)
#     # server_socket.connect((hostName, port))
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.connect((socket.gethostname(), 1234))
#     add_log(
#         "INFO", f"Server in {socketKind} in host {hostName} at port {port} is started"
#     )
#     time.sleep(1)
#     return server_socket


def send_config(server_socket: socket.socket):
    global CONFIG_DATA
    data = json.dumps(CONFIG_DATA)
    data = f"{len(data):<{HEADERSIZE}}" + data
    print(f"Trying to send {data=}")
    server_socket.send(bytes(data, "utf-8"))
    print("Data Sent")


def receive_server_config(server_socket: socket.socket):
    global server_config
    global server_config_received

    print("Waiing to receive server Config")
    server_config_len = server_socket.recv(HEADERSIZE)
    print(f"Received {server_config_len=}")
    server_config = json.loads(server_socket.recv(int(server_config_len)))
    print(f"Server Config Received\n{json.dumps(server_config, indent=4)}")
    server_config_received = True
    # listening_thread.start()


def listening_function(server_socket: socket.socket):

    global server_config_received
    while True:
        print("Listening----")
        if server_config_received:
            try:
                info_len = int(server_socket.recv(HEADERSIZE))
                info = server_socket.recv(info_len)
                print(f"{info=}")
            except:
                print("Error")
                pass
        else:
            continue


def main():
    # connect_to_server_2()
    send_config(server_socket)
    receive_server_config(server_socket)
    # listening_thread = threading.Thread(
    #     target=listening_function, args=(server_socket,)
    # )
    # listening_thread.start()


if __name__ == "__main__":
    # main()
    main()
