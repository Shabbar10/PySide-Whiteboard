import json
import socket
import msgpack

from PySide6.QtNetwork import QHostAddress, QTcpSocket, QAbstractSocket

from PySide6.QtCore import QByteArray, QDataStream, QIODevice
from client_mg import SignalManager
from WhiteboardApplication.Server.getip import get_local_ip

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
        self.data_file = {
            'scene_file': {},
            'flag': False
        }
        self.sending_list = []
        self.flag = False
        self.read_flag = False

        self.readyRead.connect(self.another_read)

    def ping_server(self, scene_info, flag):
        self.data_file = {
            'scene_info': scene_info,
            'flag': flag
        }

        if self.state() == QAbstractSocket.SocketState.ConnectedState:
            json_dump = json.dumps(self.data_file)

            block = QByteArray()
            stream = QDataStream(block, QIODevice.WriteOnly)
            stream.writeUInt32(len(json_dump))
            block.append(json_dump.encode('utf-8'))

            self.write(block)
            block.clear()

    def another_read(self):
        read_flag = True
        stream = QDataStream(self)
        try:
            while self.bytesAvailable() >= 4:
                # size = 0
            # if read_flag:
                size = stream.readUInt32()  # Read the size
                # read_flag = False
            # if self.bytesAvailable() >= size:
                data = self.read(size)  # Read the data
                # print(f"Received: {data}")
                # read_flag = True

                json_data = json.loads(data.data().decode('utf-8'))

        except Exception as e:
            print("Error decoding JSON:", e)
        else:
            signal_manager.data_ack.emit(json_data)


def start_client(client: MyClient):
    client.connectToHost(QHostAddress("192.168.29.219"), 8080)
    ip = get_local_ip()
    #client.connectToHost(QHostAddress(ip), 8080)

    # ip = get_ipv6_address()
    # client.connectToHost(QHostAddress("192.168.1.14"), 8080)
    if client.waitForConnected(8080):  # Wait for up to 5 seconds for the connection
        print("Connected to the server")
        # client.readyRead.connect(client.ping_server)

    else:
        print("Connection failed. Error:", client.errorString())