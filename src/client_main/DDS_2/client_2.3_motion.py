import socket
import threading
import json


HEADERSIZE = 5
CONFIG_DATA = {
    "id": "CLIENT_3",
    "name": "motion",
    "subscribed_topics": ["drag", "thrust", "field"],
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
    print(f"Trying to send {data=}")
    server_socket.send(format_msg_with_header(json.dumps(CONFIG_DATA)))
    print("Data Sent")


def subscribed_data_receive(msg: str):
    pass


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
                request_constants(server_socket)
            else:
                subscribed_data_receive(msg)
                print(f"subscribed_data_receive called")
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
    main()
