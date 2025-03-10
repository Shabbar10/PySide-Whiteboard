import json
import socket
from json import JSONDecodeError

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
        self.receive_buffer = QByteArray()
        self.expected_size = None

        self.readyRead.connect(self.another_read)

    def ping_server(self, scene_info, flag):
        self.data_file = {
            'scene_info': scene_info,
            'flag': flag
        }

        if self.state() == QAbstractSocket.SocketState.ConnectedState:
            json_dump = json.dumps(self.data_file)
            print(f"Json being sent: {json_dump}")
            block = QByteArray()
            stream = QDataStream(block, QIODevice.WriteOnly)
            stream.writeUInt32(len(json_dump))
            block.append(json_dump.encode('utf-8'))
            print(f"Data block being sent: {block}")
            self.write(block)
            self.flush()
            block.clear()

    def another_read(self):
        stream = QDataStream(self)

        while self.bytesAvailable():
            if self.expected_size is None:
                if self.bytesAvailable() < 4:
                    return

                self.expected_size = stream.readUInt32()

            if self.bytesAvailable() < self.expected_size:
                return

            self.receive_buffer.append(self.read(self.expected_size))
            print(f"Full data received: {self.receive_buffer}")

            try:
                json_data = json.loads(self.receive_buffer.data().decode('utf-8'))
                signal_manager.data_ack.emit(json_data)
            except JSONDecodeError as e:
                print(e)

            self.receive_buffer.clear()
            self.expected_size = None

        '''
        try:
            while self.bytesAvailable() >= 4:
                size_to_read = stream.readUInt32()  # Read the size
                print(f"Size of data coming: {size_to_read}")
                size_already_read = 0
                while self.bytesAvailable() < size_to_read:
                    pass
                data = self.read(size_to_read)  # Read the data
                print(f"Data received: {data}")
                print(f"Size of data received: {len(data)}")

                json_data = json.loads(data.data().decode('utf-8'))

        except Exception as e:
            print("Error decoding JSON:", e)
        else:
            signal_manager.data_ack.emit(json_data)
        '''


def start_client(client: MyClient):
    client.connectToHost(QHostAddress("10.20.77.115"), 8080)
    ip = get_local_ip()
    #client.connectToHost(QHostAddress(ip), 8080)

    # ip = get_ipv6_address()
    # client.connectToHost(QHostAddress("192.168.1.14"), 8080)
    if client.waitForConnected(8080):  # Wait for up to 5 seconds for the connection
        print("Connected to the server")
        # client.readyRead.connect(client.ping_server)

    else:
        print("Connection failed. Error:", client.errorString())