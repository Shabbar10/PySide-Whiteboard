import socket


def get_local_ip():
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    return ip


# print(get_local_ip())
