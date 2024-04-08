from PySide6.QtCore import QCoreApplication, QTimer, Signal
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPainterPath
from PySide6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress, QAbstractSocket
import json
from netManage import SignalManager
from getip import  get_local_ip
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
        # self.client_socket.connected.connect(lambda flag, info: self.channel_broadcast(flag, info))
        # self.client_socket.connected.connect(self.channel_broadcast)

        # self.timer = QTimer(self)
        # self.timer.timeout.connect(lambda: self.channel_broadcast(0, {}))
        # self.timer.start(4000)

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
                # print(decoded_data[0])
                # if decoded_data.strip():
                #     received_dict = json.loads(decoded_data)
                #     signal_manager.action_signal.emit(received_dict)
                #     print(received_dict)
                received_dict = json.loads(decoded_data[0])
                # json_serialized_path = self.deserialize_path(received_dict["path"])
                #
                # received_dict["path"] = json_serialized_path
                # print(json_serialized_path)
                signal_manager.data_ack.emit(received_dict)
                # print(received_dict)

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
            # Add more cases for other types like CubicToElement, etc.
        return path

    def client_disconnected(self):
        print(f"Client {self.client_address} disconnected.")

        # Allow the event loop to process events
        QCoreApplication.processEvents()


# server = myServer()


def start_server(server: MyServer):
    SERVER_IP = get_local_ip()
    server.listen(QHostAddress(SERVER_IP), 5000)
    if server.isListening():
        print("Server is listening on port 5000")
    else:
        print("Server could not start. Error:", server.errorString())


# if __name__ == "__main__":
#     app = QApplication([])
#
#     server.listen(QHostAddress("192.168.1.4"), 5000)
#     if server.isListening():
#         print("Server is listening on port 5000")
#     else:
#         print("Server could not start. Error:", server.errorString())
#
#     app.exec()
