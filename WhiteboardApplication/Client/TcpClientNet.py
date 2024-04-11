from PySide6.QtNetwork import QUdpSocket, QHostAddress, QTcpSocket, QAbstractSocket
from PySide6.QtCore import QByteArray, QCoreApplication, QTimer
import json

# Define the server address and port
SERVER_IP = "192.168.1.3"
SERVER_PORT = 8080
class MyClient(QTcpSocket):
    def __init__(self):
        super().__init__()
        self.connected.connect(self.ping_server)
        # self.connected.connect(self.get_data_from_server)
        # self.readyRead.connect(self.get_data_from_server)
        print("YES")
        self.data_file = {'scene_file' : {},
                          'flag' : False}
        print("Signal connected")
        # print("NO")
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.get_data_from_server)
        # self.timer.start(5000)

        self.a = 0

    # def connect_and_setup(self, host, port):
    #     self.connectToHost(QHostAddress(host), port)
    #     if self.waitForConnected(5000):
    #         print("Connected to the server")
    #         self.readyRead.connect(self.get_data_from_server)
    #     else:
    #         print("Connection failed. Error:", client.errorString())

    # def send_data(self):
    #     if self.state() == QAbstractSocket.SocketState.ConnectedState:
    #         self.a += 1
    #         message = "Hello from client"
    #         funcs = {'func1': [1, 2, 3],
    #                  'func2': [4, 5, "Atharva"]}
    #
    #         print("Sending dictionary ")
    #         json_data = json.dumps(funcs)
    #         decode = json_data.encode('utf-8')
    #         self.write(decode)
    #         # print(f"Sending message : {message}")
    #
    #         # self.write(message.encode("utf-8"))

    def ping_server(self, scene_info, flag):
        # print(scene_info)
        self.data_file = {
            'scene_info' : scene_info,
            'flag' : flag
        }
        # print(self.data_file)
        if self.state() == QAbstractSocket.SocketState.ConnectedState:
            # json_dump = json.dumps(scene_info)
            json_dump = json.dumps(self.data_file)

            decoded = json_dump.encode('utf-8')

            # print(decoded)
            # byte_array = QByteArray(json_dump.encode())
            self.write(decoded)




def start_client(client: MyClient):
    # try:
    client.connectToHost(QHostAddress("192.168.1.7"), 8080)
    if client.waitForConnected(8080):  # Wait for up to 5 seconds for the connection
        print("Connected to the server")
        # client.readyRead.connect(client.ping_server)
        print("T+E")

    else:
        print("Connection failed. Error:", client.errorString())
    # except Exception as e:
    #     print(f"Error during client connection: {e}")


# if __name__ == "__main__":
#     app = QCoreApplication([])
#
#     app.exec()


class UdpSock(QUdpSocket):
    def __init__(self):
        super().__init__()

    def init_client(self):
        # udp_socket = UdpSock()
        self.bind(QHostAddress(SERVER_IP), SERVER_PORT)
        self.readyRead.connect(self.ping_server)
        print(f"Client connected to server at : {SERVER_IP}")

    def ping_server(self, scene_info):
        if self.state() == QAbstractSocket.SocketState.ConnectedState:
            json_dump = json.dumps(scene_info)
            byte_array = QByteArray(json_dump.encode())
            self.writeDatagram(byte_array, QHostAddress(SERVER_IP), SERVER_PORT)



# def main() -> None:
#     udp_socket = UdpClient()
#     udp_socket.bind(QHostAddress(SERVER_IP), SERVER_PORT)
#     udp_socket.readyRead.connect(udp_socket.ping_server)
#
#
#
# main()


# timer = QTimer()
# # Create a UDP socket
# udp_socket = QUdpSocket()
#
# # Bind the socket to any available port on the local machine
# udp_socket.bind()
#
# # Send data to the server
# # def send_data():
# while KeyboardInterrupt:
#     message = "Hello, server!"
#     byte_array = QByteArray(message.encode())
#     udp_socket.writeDatagram(byte_array, QHostAddress(SERVER_IP), SERVER_PORT)
# else:
#     udp_socket.close()

# def main() -> None:
#     timer.timeout.connect(send_data)
#     timer.start(1000)

# main()
# Wait for the response from the server
# while udp_socket.waitForReadyRead():
#     data, host, port = udp_socket.readDatagram(1024)
#     print("Received message from server:", data.decode())

# Clean up resources
