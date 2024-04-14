from PySide6.QtCore import QCoreApplication, QTimer, Signal
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
        self.client_socket.readyRead.connect(self.print_data)

        self.client_socket.disconnected.connect(self.client_disconnected)
        self.client_address = self.client_socket.peerAddress().toString()
        print(f"Client connected from {self.client_address}")

    def print_data(self):
        # if self.client_socket.state() == QAbstractSocket.SocketState.ConnectedState:
        while self.client_socket.bytesAvailable() > 0:
            data_received = self.client_socket.readAll().data()
            print(
                # f"Received data from {self.client_socket.peerAddress().toString()}: {data_received.decode('utf-8')}"
            )
            try:
                decoded_data = data_received.decode('utf-8').splitlines()
                received_dict = json.loads(decoded_data[0])
                signal_manager.data_ack.emit(received_dict)

            except json.JSONDecodeError:
                print(f"Error decoding JSON: {data_received.decode('utf-8')}")

    def serialize_path(self, path):
        elements = []
        for i in range(path.elementCount()):
            element_type = path.elementAt(i).type
            if element_type == QPainterPath.MoveToElement:
                elements.append(('moveTo', (path.elementAt(i).x, path.elementAt(i).y)))
            elif element_type == QPainterPath.LineToElement:
                elements.append(('lineTo', (path.elementAt(i).x, path.elementAt(i).y)))
            # Add more cases for other types like CubicToElement, etc.
        return json.dumps(elements)

    def deserialize_path(self, serialized_data):
        path = QPainterPath()
        elements = json.loads(serialized_data)
        for element in elements:
            if element[0] == 'moveTo':
                path.moveTo(*element[1])
            elif element[0] == 'lineTo':
                path.lineTo(*element[1])
        return path

    def client_disconnected(self):
        print(f"Client {self.client_address} disconnected.")

        QCoreApplication.processEvents()


def start_server(server: MyServer):
    SERVER_IP = get_ipv6_address()
    server.listen(QHostAddress(SERVER_IP), 8080)
    if server.isListening():
        print("Server is listening on port 8080")
    else:
        print("Server could not start. Error:", server.errorString())