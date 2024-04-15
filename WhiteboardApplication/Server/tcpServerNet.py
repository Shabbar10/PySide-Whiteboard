from PySide6.QtCore import QCoreApplication, QTimer, Signal, QDataStream
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPainterPath
from PySide6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress, QAbstractSocket
import json
from netManage import SignalManager
from getip import  get_local_ip, get_ipv6_address
signal_manager = SignalManager()


class MyServer(QTcpServer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.function_call = Signal(list)
        self.data_updated = Signal(list)
        self.client_socket = None
        self.timer = None
        self.client_address = None

    def incomingConnection(self, socket_descriptor):
        print("yes\n")
        self.client_socket = QTcpSocket()
        self.client_socket.setSocketDescriptor(socket_descriptor)
        self.client_socket.readyRead.connect(lambda: self.print_data(self.client_socket))

        self.client_socket.disconnected.connect(self.client_disconnected)
        self.client_address = self.client_socket.peerAddress().toString()
        print(f"Client connected from {self.client_address}")

    def print_data(self, socket):
        while self.client_socket.bytesAvailable() > 0:
            data_received = self.client_socket.readAll().data()
            try:
                decoded_data = data_received.decode('utf-8')
                print(f"Size of decoded data is {decoded_data.__sizeof__()}")
                if decoded_data[0] == '{':
                    for i in range(len(decoded_data)):
                        if decoded_data[i] == '}' and (i+1) != len(decoded_data):
                            if decoded_data[i+1] == '{':
                                end_index = i+1
                                decoded_data = decoded_data[:end_index]
                                break

                    received_dict = json.loads(decoded_data)
                    signal_manager.data_ack.emit(received_dict)

            except json.JSONDecodeError as e:
                '''
                print(f"Error decoding JSON: {data_received.decode('utf-8')}")
                print(f"Error msg: {e.msg}")
                print(f"Input document: {e.doc}")
                print(f"Position in document: {e.pos}")
                '''
                pass

    def client_disconnected(self):
        print(f"Client {self.client_address} disconnected.")

        QCoreApplication.processEvents()


def start_server(server: MyServer):
    SERVER_IP = get_local_ip()
    server.listen(QHostAddress(SERVER_IP), 8080)
    if server.isListening():
        print("Server is listening on port 8080", SERVER_IP)
    else:
        print("Server could not start. Error:", server.errorString())