import json
import socket
from json import JSONDecodeError

import msgpack

from PySide6.QtNetwork import QHostAddress, QTcpSocket, QAbstractSocket

from PySide6.QtCore import QByteArray, QDataStream, QIODevice, QObject, Signal, QThread
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

class NetworkWorker(QObject):
    connection_status = Signal(bool)
    connect = Signal(str, int) # host, port
    send_data_signal = Signal(dict, bool)

    def __init__(self):
        super().__init__()
        self.send_data_signal.connect(self.handle_send)
        self.connect.connect(self.connect_to_host)

    def setup_client(self):
        self.client = QTcpSocket()
        self.client.connected.connect(self.on_connected)
        self.client.disconnected.connect(self.on_disconnected)
        self.client.readyRead.connect(self.handle_read)

        self.receive_buffer = QByteArray()
        self.expected_size = None

    def connect_to_host(self, host, port):
        self.client.connectToHost(QHostAddress(host), port)
        if not self.client.waitForConnected(5000):
            self.connection_status.emit(False)

    def on_connected(self):
        print("Connected to server")
        self.connection_status.emit(True)

    def on_disconnected(self):
        print("Disconnected from server")
        self.connection_status.emit(False)

    def handle_send(self, scene_info, flag):
        if self.client.state() != QAbstractSocket.SocketState.ConnectedState:
            print("Socket not connected")
            return

        data_file = {
            'scene_info': scene_info,
            'flag': flag
        }

        try:
            json_dump = json.dumps(data_file)
            block = QByteArray()
            stream = QDataStream(block, QIODevice.WriteOnly)
            stream.writeUInt32(len(json_dump))
            block.append(json_dump.encode('utf-8'))

            self.client.write(block)
            self.client.flush()
        except Exception as e:
            print(e)

    def handle_read(self):
        stream = QDataStream(self.client)

        while self.client.bytesAvailable():
            if self.expected_size is None:
                if self.client.bytesAvailable() < 4:
                    return

                self.expected_size = stream.readUInt32()

            if self.client.bytesAvailable() < self.expected_size:
                break

            data = self.client.read(self.expected_size)
            self.receive_buffer.append(data)

            try:
                message_data = self.receive_buffer.data().decode('utf-8')
                json_data = json.loads(message_data)
                signal_manager.data_ack.emit(json_data)
            except JSONDecodeError as e:
                print(f"JSON decode error: {e}")
            finally:
                self.receive_buffer.clear()
                self.expected_size = None


class MyClient(QTcpSocket):
    def __init__(self):
        super().__init__()
        self.thread = QThread()
        self.worker = NetworkWorker()
        self.worker.moveToThread(self.thread)
        self.thread.start()

    def connect_to_server(self, host, port):
        self.worker.connect.emit(host, port)

    def send_data(self, scene_info, flag):
        self.worker.send_data_signal.emit(scene_info, flag)


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