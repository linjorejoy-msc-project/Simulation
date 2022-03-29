import socket
import time

HEADERSIZE = 5

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect((socket.gethostname(), 1234))


def connect_to_server():
    while True:
        full_msg = ""
        new_msg = True
        while True:
            msg = server_socket.recv(16)
            print(f"{msg=}")
            if new_msg:
                print(f"Msg len = {msg[:HEADERSIZE]}")
                msglen = int(msg[:HEADERSIZE])
                new_msg = False

            full_msg += msg.decode("utf-8")
            if len(full_msg) - HEADERSIZE == msglen:
                print(f"Full msg recd : {full_msg=}")
                new_msg = True
                full_msg = ""
                # full_msg = f"{len(new_msg):<{HEADERSIZE}}" + new_msg

                reply_msg = f"Message received at {time.time()}"
                reply_msg = f"{len(reply_msg):<{HEADERSIZE}}" + reply_msg
                server_socket.send(bytes(reply_msg, "utf-8"))


def connect_to_server_2():
    try:
        count = 0
        while True:
            time.sleep(1)
            msg = f"The current time is {time.time()}"
            msg = f"{len(msg):<{HEADERSIZE}}" + msg
            server_socket.send(bytes(msg, "utf-8"))
            print(f"{'SENDING':<10}: {msg=}")
            # while True:
            #     count += 1
            #     header_data = server_socket.recv(HEADERSIZE)
            #     reply_msg_len = int(header_data)
            #     data = server_socket.recv(reply_msg_len).decode("utf-8")
            #     print(f"{'RECEIVED':<10}: {data=} at {time.time()}")
            #     print(f"{count=}")
            #     if count > 5:
            #         server_socket.close()
            #         break
            #     if reply_msg_len > 0:
            #         break

    except ConnectionResetError:
        print(f"Server Connection was closed")


def main():
    # connect_to_server()
    connect_to_server_2()


if __name__ == "__main__":
    main()
