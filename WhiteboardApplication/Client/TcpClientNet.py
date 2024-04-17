import json
import socket
import msgpack

from PySide6.QtNetwork import QHostAddress, QTcpSocket, QAbstractSocket
from PySide6.QtCore import QUrl, QThread
from PySide6.QtWebSockets import QWebSocket
from client_mg import SignalManager

signal_manager = SignalManager()


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
        self.data_file = {'scene_file': {},
                          'flag': False}
        print("Signal connected")
        self.sending_list = []
        self.flag = False

        self.readyRead.connect(self.read_data)

    def ping_server(self, scene_info, flag):
        self.data_file = {
            'scene_info': scene_info,
            'flag': flag
        }

        self.sending_list.append(self.data_file)

        if len(self.sending_list) > 1:  # Once list has 2 dictionaries, set flag
            self.flag = True

        if self.flag:
            if self.state() == QAbstractSocket.SocketState.ConnectedState:
                # json_dump = json.dumps(self.data_file)

                # encoded = json_dump.encode('utf-32')
                encoded = msgpack.packb(self.sending_list.pop(0))
                # self.list_index = (self.list_index + 1) % 5

                self.write(encoded)

    def read_data(self):
        data = self.readAll().data()

        try:
            # decoded_data = data.decode('utf-32')
            decoded_data = msgpack.unpackb(data)
            print(decoded_data)
            '''
            if decoded_data[0][0] == '{':
                for i in range(len(decoded_data[0])):
                    if decoded_data[0][i] == '}' and (i+1) != len(decoded_data[0]):
                        if decoded_data[0][i+1] == '{':
                            end_index = i+1
                            decoded_data[0] = decoded_data[0][:end_index]
                            break
            received_dict = json.loads(decoded_data[0])
            '''
            # signal_manager.data_ack.emit(decoded_data)

        # except json.JSONDecodeError as e:
        except Exception as e:
            print(e)
            '''
            print(f"Error msg: {e.msg}")
            print(f"Input document: {e.doc}")
            print(f"Position in document: {e.pos}")
            '''


def start_client(client: MyClient):
    # ip = get_ipv6_address()
    client.connectToHost(QHostAddress("192.168.112.82"), 8080)
    if client.waitForConnected(8080):  # Wait for up to 5 seconds for the connection
        print("Connected to the server")
        # client.readyRead.connect(client.ping_server)
        print("T+E")

    else:
        print("Connection failed. Error:", client.errorString())
