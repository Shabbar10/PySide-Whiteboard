import redis
import subprocess
from PySide6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress, QAbstractSocket
from PySide6.QtCore import QCoreApplication
import json
from getip import get_local_ip
from netManage import SignalManager
from PySide6.QtCore import QCoreApplication, QTimer, Signal

signalmg = SignalManager()


class MyServer2(QTcpServer):
    def __init__(self):
        super().__init__()
        self.timer = None
        self.counter = 0
        self.clients = []
        self.client_socket = []
        self.database_signal = Signal(str, str)
        self.redis_host = 'localhost'
        self.redis_port = 6379

    def incomingConnection(self, socket_descriptor):
        socket = QTcpSocket()
        socket.setSocketDescriptor(socket_descriptor)

        socket.readyRead.connect(self.on_connected)
        socket.disconnected.connect(self.on_disconnected)
        print(f"Client connected from {socket.peerAddress().toString()}")

        self.client_socket.append(socket)
        self.clients.append(socket.peerAddress().toString())

        print("Yes")

    def on_connected(self):
        socket = self.sender()
        ip_add = socket.peerAddress().toString()
        self.counter += 1

        print(ip_add)
        username = "User" + str(self.counter)
        print("Update DB called")
        try:
            r = redis.StrictRedis(host=self.redis_host, port=self.redis_port, decode_responses=True)
            # r.set('India', 'Mumbai')
            r.hset(username, 'IP', ip_add)
            print(f"Registered User : {r.hgetall(username)}")

        except Exception as e:
            print(f"ERROR OCCURRED : {e}")
        # self.database_signal.emit(username, ip_add)

    def update_db(self, username: str, ip: str):
        print("Update DB called")
        try:
            r = redis.StrictRedis(host=self.redis_host, port=self.redis_port, decode_responses=True)
            # r.set('India', 'Mumbai')
            r.hset(username, 'IP', ip)
            print(f"Registered User : {r.hgetall(username)}")

        except Exception as e:
            print(f"ERROR OCCURRED : {e}")

    def read_from_db(self):
        pass

    def on_disconnected(self):
        socket = self.sender()
        if not isinstance(socket, QTcpSocket):
            return
        print(f"Client {socket.peerAddress().toString()} disconnected.")

        # Allow the event loop to process events
        # QCoreApplication.processEvents()


def start_server(server: MyServer2):
    SERVER_IP = get_local_ip()
    server.listen(QHostAddress(SERVER_IP), 8080)
    if server.isListening():
        print("Server is listening on port 5000, IP : ", SERVER_IP)
    else:
        print("Server could not start. Error:", server.errorString())


if __name__ == "__main__":
    app = QCoreApplication([])
    local_server = MyServer2()
    signalmg.send_info2.connect(local_server.update_db)

    start_server(local_server)
    app.exec()