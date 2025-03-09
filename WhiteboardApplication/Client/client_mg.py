from PySide6.QtCore import QObject, Signal


class SignalManager(QObject):
    # List of signals that would be used to exchange data between objects
    def __init__(self):
        super(SignalManager, self).__init__()

    function_call = Signal(bool) # Call scene_file if undo/redo
    data_updated = Signal(list) # Call scene_file if new shape is drawn
    data_serialized = Signal(dict, bool) # Now send to server

    send_info = Signal(str, str)
    action_signal = Signal(dict)
    data_ack = Signal(dict)
    login_verify = Signal(bool)

    def update_data(self, data):
        self.data_updated.emit(data)