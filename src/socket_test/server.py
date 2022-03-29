import socket
import time

HEADERSIZE = 5

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((socket.gethostname(), 1234))
server_socket.listen(5)


def connect_to_client():
    while True:
        client_socket, address = server_socket.accept()
        print(f"Connection with {client_socket=} with {address=} is established")

        msg = "This is te first connection"
        msg = f"{len(msg):<{HEADERSIZE}}" + msg

        client_socket.send(bytes(msg, "utf-8"))

        while True:
            reply_full_msg = ""
            new_msg = True
            while True:
                reply_msg = client_socket.recv(16)
                print(f"{reply_msg=}")
                if new_msg:
                    print(f"Msg len = {reply_msg[:HEADERSIZE]}")
                    reply_msglen = int(reply_msg[:HEADERSIZE])
                    new_msg = False
                reply_full_msg += reply_msg.decode("utf-8")
                if len(reply_full_msg) - HEADERSIZE == reply_msglen:
                    print(f"Full msg recd : {reply_full_msg=}")
                    new_msg = True
                    reply_full_msg = f"{len(new_msg):<{HEADERSIZE}}" + new_msg


def connect_to_client_2():
    while True:
        client_socket, address = server_socket.accept()
        print(f"Connection with {client_socket=} with {address=} is established")
        count = 0
        while True:
            print("This while loop starting")
            count += 1
            header_data = client_socket.recv(HEADERSIZE)
            msg_len = int(header_data)
            data = client_socket.recv(msg_len)
            data = data.decode("utf-8")
            print(f"{'RECEIVED':<10}: {data=} at {time.time()}")
            reply_msg = f"Msg was received at time :{time.time()}"
            reply_msg = f"{len(reply_msg):<{HEADERSIZE}}" + reply_msg
            client_socket.send(bytes(reply_msg, "utf-8"))
            print(f"{'SENDING':<10}: {reply_msg=}")
            print(f"{count=}")
            # if count >= 5:
            #     print("Closing----")
            # client_socket.shutdown(socket.SHUT_RDWR)
            # client_socket.close()
            # server_socket.shutdown(socket.SHUT_RD)
            # server_socket.close()
            # break
        break


def main():
    # connect_to_client()
    connect_to_client_2()


if __name__ == "__main__":
    main()
