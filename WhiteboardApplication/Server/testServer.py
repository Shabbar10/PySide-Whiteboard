import redis
from PySide6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from getip import get_local_ip
from netManage import SignalManager
from PySide6.QtCore import QCoreApplication, Signal, QDataStream, QByteArray, QIODevice

signal_manager = SignalManager()


class MyServer(QTcpServer):
    def __init__(self):
        super().__init__()
        self.timer = None
        self.counter = 0
        self.clients = []
        self.client_socket = []
        self.database_signal = Signal(str, str)
        redis_host = 'localhost'
        redis_port = 6379

        self.r = redis.StrictRedis(redis_host, redis_port, decode_responses=True)
        # Set data in Redis
        self.r.set('Atharva', 'ghanekar')
        self.r.set('Abubakar', 'siddiq')
        self.r.set('Shabbar', 'adamjee')
        self.r.set('Hussain', 'ceyloni')



    def incomingConnection(self, socket_descriptor):
        socket = QTcpSocket()
        socket.setSocketDescriptor(socket_descriptor)

        self.counter += 1
        username = "User" + str(self.counter)
        self.r.hset(username, 'IP', socket.peerAddress().toString())


        self.client_socket.append(socket)
        for each_socket in self.client_socket:
            each_socket.readyRead.connect(lambda: self.on_connected(each_socket))

        socket.disconnected.connect(self.on_disconnected)


    def on_connected(self, sender : QTcpSocket):
        sender_ip = sender.peerAddress().toString()
        stream = QDataStream(sender)
        block = QByteArray()

        if sender.bytesAvailable() < 4:
            return
        size_to_read = stream.readUInt32()
        #if sender.bytesAvailable() < size_to_read:
            #return
        data = sender.read(size_to_read)
        print(f"Data received: {data}")

        send_stream = QDataStream(block, QIODevice.WriteOnly)
        send_stream.writeUInt32(size_to_read)
        block.append(data)

        print(f"Sender IP: {sender_ip}")
        for each_socket in self.client_socket:
            #if each_socket.peerAddress().toString() != sender_ip:
            each_socket.write(block)

    def on_disconnected(self):
        socket = self.sender()
        if not isinstance(socket, QTcpSocket):
            return
        print(f"Client {socket.peerAddress().toString()} disconnected.")

        # Allow the event loop to process events
        # QCoreApplication.processEvents()


def start_server(server: MyServer):
    SERVER_IP = get_local_ip()
    server.listen(QHostAddress(SERVER_IP), 8080)
    if server.isListening():
        print("Server is listening on port 8080, IP : ", SERVER_IP)
    else:
        print("Server could not start. Error:", server.errorString())


if __name__ == "__main__":
    app = QCoreApplication([])
    local_server = MyServer()

    start_server(local_server)
    app.exec()
