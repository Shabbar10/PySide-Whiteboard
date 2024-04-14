import json
import socket

from PySide6.QtNetwork import QHostAddress, QTcpSocket, QAbstractSocket


def get_ipv6_address():
    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

    try:
        s.connect(("ipv6.google.com", 80))
        global_ipv6_address = s.getsockname()[0]

        return global_ipv6_address
    except Exception as e:
        print("Error:", e)
    finally:
        s.close()


class MyClient(QTcpSocket):
    def __init__(self):
        super().__init__()
        self.connected.connect(self.ping_server)
        print("YES")
        self.data_file = {'scene_file': {},
                          'flag': False}
        print("Signal connected")

        self.a = 0

    def ping_server(self, scene_info, flag):
        # print(scene_info)
        self.data_file = {
            'scene_info': scene_info,
            'flag': flag
        }
        # print(self.data_file)
        if self.state() == QAbstractSocket.SocketState.ConnectedState:
            # json_dump = json.dumps(scene_info)
            json_dump = json.dumps(self.data_file)

            decoded = json_dump.encode('utf-8')

            # print(decoded)
            # byte_array = QByteArray(json_dump.encode())
            self.write(decoded)


def start_client(client: MyClient):
    ip = get_ipv6_address()
    client.connectToHost(QHostAddress(ip), 8080)
    if client.waitForConnected(8080):  # Wait for up to 5 seconds for the connection
        print("Connected to the server")
        # client.readyRead.connect(client.ping_server)
        print("T+E")

    else:
        print("Connection failed. Error:", client.errorString())
