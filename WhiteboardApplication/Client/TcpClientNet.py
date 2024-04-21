import json
import socket
import msgpack

from PySide6.QtNetwork import QHostAddress, QTcpSocket, QAbstractSocket

from PySide6.QtCore import QByteArray, QDataStream, QIODevice
from client_mg import SignalManager
import threading

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
        self.data_file = {'scene_file': {},
                          'flag': False}
        print("Signal connected")
        self.sending_list = []
        self.flag = False
        self.read_flag = False



        # self.readyRead.connect(self.read_data)
        self.readyRead.connect(self.another_read)




    def ping_server(self, scene_info, flag):
        self.data_file = {
            'scene_info': scene_info,
            'flag': flag
        }

        if self.state() == QAbstractSocket.SocketState.ConnectedState:
            json_dump = json.dumps(self.data_file)

            block = QByteArray()
            stream = QDataStream(block, QIODevice.WriteOnly)
            print(f"Size: {len(json_dump)}")
            stream.writeUInt32(len(json_dump))
            block.append(json_dump.encode('utf-8'))

            # if self.flag:
            #     if self.state() == QAbstractSocket.SocketState.ConnectedState:
            #         # json_dump = json.dumps(self.data_file)
            #         # encoded = json_dump.encode('utf-32')
            #         encoded = msgpack.packb(self.sending_list.pop(0))
            #         print("Encoded length : ", len(encoded))
            #         # self.list_index = (self.list_index + 1) % 5
            #
            #         self.write(encoded)
            print(f"Block: {block}")
            self.write(block)
            # self.flush()
            block.clear()
            # print(f"{len(json_dump)} : {self.data_file}")



    def read_data(self):
        next_size = 0
        try:
            if not self.read_flag:
                data = self.readAll().data()
                print(f"The received size is {data.__sizeof__()}")
                decoded_data = msgpack.unpackb(data)
                # print(decoded_data)
                next_size = decoded_data['next_size']
                self.read_flag = True
            else:
                data = self.read(next_size).data()
                decoded_data = msgpack.unpackb(data)

            # print(f"Next size is {next_size}")
            '''
            if decoded_data[0][0] == '{':
                for i in range(len(decoded_data[0])):
                    if decoded_data[0][i] == '}' and (i+1) != len(decoded_data[0]):
                        if decoded_data[0][i+1] == '{':
                            end_index = i+1
                            decoded_data[0] = decoded_data[0][:end_index]
                            break
            received_dict = json.loads(decoded_data[0])
            '''
            print(f"This is what I've decoded: {decoded_data}")
            signal_manager.data_ack.emit(decoded_data)

        # except json.JSONDecodeError as e:
        except Exception as e:
            print(e)
            # print(e)

    def another_read(self):
        read_flag = True
        stream = QDataStream(self)
        try:
            while self.bytesAvailable() >= 4:
                # size = 0
            # if read_flag:
                size = stream.readUInt32()  # Read the size
                print(f"Size: {size}")
                # read_flag = False
            # if self.bytesAvailable() >= size:
                data = self.read(size)  # Read the data
                # print(f"Received: {data}")
                # read_flag = True

                json_data = json.loads(data.data().decode('utf-8'))
                # signal_manager.data_ack.emit(json_data)

        except Exception as e:
            print("Error decoding JSON:", e)
        else:
            signal_manager.data_ack.emit(json_data)
            # self.flush()
            # Handle the decoding error, such as logging or ignoring the data
        # while self.bytesAvailable() > 0:
        #     if self.bytesAvailable() < 4:  # If no int of size is there
        #         # return
        #         print("Size less than 4 bytes")
        #         break
        #
        #     size = stream.readUInt32()  # read the size
        #     print(f"Size: {size}")
        #     try:
        #         while True:
        #             if self.bytesAvailable() < size:  # if amount of data is not enough
        #                 continue
        #             else:
        #                 data = self.read(size)
        #                 # print(data)
        #                 json_data = json.loads(data.data().decode('utf-8'))
        #                 signal_manager.data_ack.emit(json_data)
        #                 break
        #     except Exception as e:
        #         print(e)


def start_client(client: MyClient):
    # ip = get_ipv6_address()
    # client.connectToHost(QHostAddress("192.168.201.204"), 8080)
    client.connectToHost(QHostAddress("192.168.1.14"), 8080)

    # ip = get_ipv6_address()
    # client.connectToHost(QHostAddress("192.168.1.14"), 8080)
    if client.waitForConnected(8080):  # Wait for up to 5 seconds for the connection
        print("Connected to the server")
        # client.readyRead.connect(client.ping_server)

    else:
        print("Connection failed. Error:", client.errorString())