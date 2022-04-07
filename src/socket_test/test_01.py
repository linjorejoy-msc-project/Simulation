from client_main.DDS_2.common_functions import check_to_run_cycle

dictionary = {"a": False, "b": False, "c": True}


print(check_to_run_cycle(dictionary))


# Logging
# import logging
# import os

# file_path = os.path.join(os.path.abspath(os.curdir), "src\\client_main\\LOGS")
# FORMAT = "%(levelname)-10s %(asctime)s: %(message)s"
# logging.basicConfig(
#     filename=f"{file_path}\\logs2.log",
#     encoding="utf-8",
#     level=logging.DEBUG,
#     format=FORMAT,
# )

# logging.info("Smtg")
# Logging end


# import os

# print(os.path.abspath(os.curdir))


# from client_main.DDS_2.common_functions import format_msg_with_header_and_topic
# data = format_msg_with_header_and_topic("topic", "Hello")
# print(data.decode("utf-8"))  # 30   topic                    Hello

# print(data[5:30].strip().decode("utf-8"))


# import socket

# PORT = 5050
# SERVER = socket.gethostbyname(socket.gethostname())

# print(SERVER)
