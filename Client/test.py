from PySide6.QtCore import Qt, QCoreApplication, QTimer
from PySide6.QtNetwork import QTcpSocket, QHostAddress, QAbstractSocket
import json
from client_mg import SignalManager

signal_manager = SignalManager()


def pen_cap_style_to_str(cap_style):
    return str(cap_style)

def str_to_pen_cap_style(value):
    return Qt.PenCapStyle[value]

def pen_join_style_to_str(join_style):
    return str(join_style)

def str_to_pen_join_style(value):
    return Qt.PenJoinStyle[value]

def pen_style_to_str(pen_style):
    return str(pen_style)

def str_to_pen_style(value):
    return Qt.PenStyle[value]


class MyClient(QTcpSocket):
    def __init__(self):
        super().__init__()
        # self.connected.connect(self.send_data)
        self.readyRead.connect(self.get_data_from_server)

        """self.timer = QTimer(self)
        self.timer.timeout.connect(self.get_data_from_server)
        self.timer.start(5000)"""

        self.a = 0

    def get_data_from_server(self):
        data_recv = self.readAll().data()
        self.process_data(data_recv)

    def process_data(self, data_recv):
        json_strings = data_recv.decode('utf-8').split('\n')

        for json_str in json_strings:
            if json_str.strip():
                json_obj = json.loads(json_str)
                print(json_obj)
                x, y = json_obj[1], json_obj[0]
                signal_manager.retrace.emit(x, y)

        self.printACK("Yes!")

        # for keys, args in func_dict.items():
        #     if keys == 'printACK':
        #          arg = func_dict[keys]
        #          self.printACK(arg)

    def printACK(self, msg):
        print(f"Printing ACK: {msg}")

    def get_data_from_server(self):
        info_recv = self.readAll().data()
        json_string = info_recv.decode('utf-8').split('\n')
        scene_info = {}
        for eachString in json_string:
            if eachString.strip():
                scene_info = json.loads(eachString)

                print(scene_info)

        signal_manager.retrace_canvas.emit(scene_info)


def start_client(client: MyClient):
    try:
        client.connectToHost(QHostAddress("192.168.67.1"), 5000)
        if client.waitForConnected(5000):  # Wait for up to 5 seconds for the connection
            print("Connected to the server")
        else:
            print("Connection failed. Error:", client.errorString())
    except Exception as e:
        print(f"Error during client connection: {e}")


if __name__ == "__main__":
    app = QCoreApplication([])

    app.exec()
