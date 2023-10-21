# WORK IN PROGRESS

#---------------------------------------------

# With f1_2020_telemetry library:

# import socket

# from f1_2020_telemetry.packets import unpack_udp_packet

# udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# udp_socket.bind(("", 20777))

# while True:
#     udp_packet = udp_socket.recv(2048)
#     packet = unpack_udp_packet(udp_packet)
#     print("Received:", packet)
#     print()

#---------------------------------------------

# Without f1_2020_telemetry library (needs unpacking):

# import socket

# udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# udp_socket.bind(("", 20777))

# while True:
#     udp_packet = udp_socket.recv(2048)
#     print("Received:", udp_packet)
#     print()
