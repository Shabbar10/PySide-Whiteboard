from PySide6.QtCore import QCoreApplication, QTimer, Signal
from PySide6.QtWidgets import QApplication
from PySide6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress, QAbstractSocket
import json
from netManage import SignalManager

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
        # self.client_socket.readyRead.connect(lambda: self.process_data(self.client_socket))
        self.client_socket.connected.connect(lambda flag, info: self.channel_broadcast(flag, info))

        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.channel_broadcast(0, {}))
        self.timer.start(4000)

        self.client_socket.disconnected.connect(self.client_disconnected)
        self.client_address = self.client_socket.peerAddress().toString()
        print(f"Client connected from {self.client_address}")

    def send_data(self, coord):
        if self.client_socket:
            if self.client_socket.state() == QAbstractSocket.SocketState.ConnectedState:
                # self.a += 1
                # message = "Acknowledgement from server"
                print("Sending Data\n\n")
                # dict = {'printACK' : 'Received data from Server'}
                print(coord)
                # print(f"Sending message : {message}")
                # self.write(message.encode("utf-8"))
                data_to_dump = json.dumps(coord) + "\n"
                self.client_socket.write(data_to_dump.encode('utf-8'))
                # data_to_dump = {}

        else:
            print("Client socket is not connected yet.")

    def broadcast(self, render_info: dict):
        print(render_info)

    # @staticmethod
    def channel_broadcast(self, flag: int, usage_info: dict):

        if type(flag) is not int or type(usage_info) is not dict:
            print("error")

        else:
            # if flag == 1:
                # If flag = 1 -> It is an action such as save , open or close which is restricted to client-server
                # communication and the info should not be broadcasted to other clients

                # pass
            if self.client_socket:
                # print(f"{flag}\t {usage_info}\n")
                if self.client_socket.state() == QAbstractSocket.SocketState.ConnectedState:
                    usage_data = json.dumps(usage_info) + "\n"
                    self.client_socket.write(usage_data.encode('utf-8'))



    def process_data(self, client_socket):
        if client_socket.bytesAvailable() > 0:
            data_received = client_socket.readAll().data()
            print(
                f"Received data from {client_socket.peerAddress().toString()}: {data_received.decode('utf-8')}"
            )
            decoded_data = data_received.decode('utf-8')

            received_dict = json.loads(decoded_data)

            # for func in received_list:
            #     if func == "func1":
            #         self.func1()
            #     if func == "func2":
            #         self.func2()
            #     # self.function_call.connect(self.func)

            for func_name, arguments in received_dict.items():
                if func_name == 'func1':
                    arg1, arg2, arg3 = received_dict[func_name]
                    # arg_list =
                    self.func1(arg1, arg2, arg3)
                if func_name == 'func2':
                    arg1, arg2, arg3 = received_dict[func_name]
                    self.func2(arg1, arg2, arg3)

            client_socket.write(data_received)

    def func1(self, arg1, arg2, arg3):
        print(f"Slot 1 function working\n Arguments are {arg1} , {arg2} , {arg3}")

    def func2(self, arg1, arg2, arg3):
        print(f"Slot 1 function working\n Arguments are {arg1} , {arg2} , {arg3}")

    def client_disconnected(self):
        print(f"Client {self.client_address} disconnected.")

        # Allow the event loop to process events
        QCoreApplication.processEvents()


# server = myServer()


def start_server(server: MyServer):
    server.listen(QHostAddress("192.168.67.1"), 5000)
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
