from PySide6.QtCore import QObject, Signal


class SignalManager(QObject):
    # List of signals that would be used to exchange data between objects
    def __init__(self):
        super(SignalManager, self).__init__()

    function_call = Signal(bool)
    data_updated = Signal(list)
    receive_data = Signal(int, int)
    send_info = Signal(dict)
    send_info2 = Signal(str, str)

    action_signal = Signal(dict)
    data_sig = Signal(dict, bool)
    data_ack = Signal(dict)
    login_verify = Signal(bool)

    def update_data(self, data):
        self.data_updated.emit(data)
