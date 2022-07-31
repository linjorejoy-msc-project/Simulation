import time
from client_main.DDS_2.common_functions import (
    format_msg_with_header,
    recv_topic_data,
)

# start = time.perf_counter_ns()
# time.sleep(0.5)
# end = time.perf_counter_ns()

# print(f"{start=} and {len(str(start))=}")
# print(end)
# print(end - start)


recv_msg_data = (
    '75   thrust                   338112176828100     {"currentThrust": 123191000.0}'
)
recv_msg_data = recv_msg_data[5:]
TOPICLABELSIZE = 25
TIMEDATASIZE = 20

topic = "drag"
data = "dadadas"

msgToSend = (
    f"{topic:{TOPICLABELSIZE}}{str(time.perf_counter_ns()):{TIMEDATASIZE}}{data}"
)
formatted_msg = format_msg_with_header(msgToSend)
print(formatted_msg)

received_msg = formatted_msg.decode("utf-8")[5:]
output = (
    str(received_msg[:TOPICLABELSIZE]).strip(),
    int(str(received_msg[TOPICLABELSIZE : TOPICLABELSIZE + TIMEDATASIZE]).strip()),
    received_msg[TOPICLABELSIZE + TIMEDATASIZE :],
)
output = (
    str(recv_msg_data[:TOPICLABELSIZE]).strip(),
    int(str(recv_msg_data[TOPICLABELSIZE : TOPICLABELSIZE + TIMEDATASIZE]).strip()),
    recv_msg_data[TOPICLABELSIZE + TIMEDATASIZE :],
)
print(output)
# recv_topic
