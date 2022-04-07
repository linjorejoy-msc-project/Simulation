import socket
import threading
from time import sleep

from client_main.DDS_2.common_functions import format_msg_with_header, recv_msg


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect((socket.gethostname(), 1235))

NAME = "CL_3"


def listening_func():
    while True:
        msg = recv_msg(server_socket)
        if msg:
            print(msg)


def sending_function():
    while True:
        server_socket.send(format_msg_with_header(f"{NAME} : Hai"))


def main():
    listening_thread = threading.Thread(target=listening_func)
    sending_thread = threading.Thread(target=sending_function)
    listening_thread.start()
    sending_thread.start()


if __name__ == "__main__":
    main()
