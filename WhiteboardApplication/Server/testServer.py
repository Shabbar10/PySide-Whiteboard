# import redis
from PySide6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from getip import get_local_ip
from netManage import SignalManager
from PySide6.QtCore import QCoreApplication, Signal, QDataStream, QByteArray, QIODevice, QThread
import socket
import pyaudio
import threading

signal_manager = SignalManager()

import socket
import pyaudio
import threading

class VoiceServer:
    def __init__(self, port=5000):
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, output=True, frames_per_buffer=self.CHUNK)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", port))
        self.server_socket.listen(5)
        self.clients = []

    def handle_client(self, client_socket):
        """Handles incoming voice data from a client."""
        while True:
            try:
                data = client_socket.recv(self.CHUNK)
                if not data:
                    break
                print(f"[SERVER] Received voice input from {client_socket.getpeername()}")

                # Broadcast to other clients
                for client in self.clients:
                    if client != client_socket:
                        try:
                            client.sendall(data)
                            print(f"[SERVER] Forwarded voice to {client.getpeername()}")
                        except:
                            print(f"[WARNING] Failed to send to {client.getpeername()}, removing from list")
                            self.clients.remove(client)

            except Exception as e:
                print(f"[SERVER] Client Disconnected: {e}")
                break

        if client_socket in self.clients:
            self.clients.remove(client_socket)
        client_socket.close()

    def accept_clients(self):
        print("Voice server started on port 5000")
        while True:
            client_socket, _ = self.server_socket.accept()
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()


class MyServer(QTcpServer):
    def __init__(self):
        super().__init__()
        self.timer = None
        self.counter = 0
        self.clients = []
        self.client_socket = []
        self.database_signal = Signal(str, str)
        # redis_host = 'localhost'
        # redis_port = 6379

        # self.r = redis.StrictRedis(redis_host, redis_port, decode_responses=True)
        # Set data in Redis
        # self.r.set('Atharva', 'ghanekar')
        # self.r.set('Abubakar', 'siddiq')
        # self.r.set('Shabbar', 'adamjee')
        # self.r.set('Hussain', 'ceyloni')



    def incomingConnection(self, socket_descriptor):
        socket = QTcpSocket()
        socket.setSocketDescriptor(socket_descriptor)

        # thread = QThread()
        # socket.moveToThread(thread)
        #
        # thread.started.connect(self.handle_client)
        # thread.start()
        self.client_socket.append(socket)
        for each_socket in self.client_socket:
            each_socket.readyRead.connect(lambda: self.on_connected(each_socket))

        socket.disconnected.connect(self.on_disconnected)

    def handle_client(self, socket : QTcpSocket):
        self.counter += 1
        username = "User" + str(self.counter)
        print(f"{username} connected")
        # self.r.hset(username, 'IP', socket.peerAddress().toString())

        socket.readyRead.connect(lambda: self.on_connected(socket))
        socket.disconnected.connect(lambda: self.on_disconnected(socket))


    def on_connected(self, sender : QTcpSocket):
        sender_ip = sender.peerAddress().toString()
        stream = QDataStream(sender)
        block = QByteArray()

        if sender.bytesAvailable() < 4:
            return
        size_to_read = stream.readUInt32()
        print(f"Size: {size_to_read}")
        #if sender.bytesAvailable() < size_to_read:
            #return
        data = sender.read(size_to_read)
        # print(f"Data received: {data}")

        send_stream = QDataStream(block, QIODevice.WriteOnly)
        send_stream.writeUInt32(size_to_read)
        block.append(data)

        # print(f"Sender IP: {sender_ip}")
        for each_socket in self.client_socket:
            if each_socket.peerAddress().toString() != sender_ip:
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

    voice_server = VoiceServer()  # Initialize voice chat server
    threading.Thread(target=voice_server.accept_clients, daemon=True).start()

    start_server(local_server)
    app.exec()
