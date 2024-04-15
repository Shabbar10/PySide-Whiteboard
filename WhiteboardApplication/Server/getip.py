import socket


def get_local_ip():
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    return ip


def get_ipv6_address():
    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

    try:
        s.connect(("ipv6.google.com", 80))
        global_ipv6_address = s.getsockname()[0]

        print(f"Global IPv6 address: {global_ipv6_address}")
        return global_ipv6_address
    except Exception as e:
        print("Error:", e)
    finally:
        s.close()
