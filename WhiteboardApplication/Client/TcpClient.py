import sys

from PySide6.QtWidgets import (
    QMainWindow,
    QGraphicsScene,
    QApplication,
    QGraphicsPathItem,
    QColorDialog,
    QFileDialog,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QGraphicsEllipseItem,
    QGraphicsRectItem
)

from PySide6.QtGui import (
    QPen,
    Qt,
    QPainter,
    QPainterPath,
    QColor,
    QPalette,
    QLinearGradient,
    QFont
)

from PySide6.QtCore import (
    Qt,
    QTimer,
    QRectF
)
import json
from TcpClientNet import start_client, MyClient, signal_manager
from WhiteboardApplication.UI.board import Ui_MainWindow
from collections import deque

itemTypes = set()
circular_recv_buffer = deque(maxlen=20)
circular_send_buffer = deque(maxlen=20)
buffer_flag = 0
g_length = 0
login_flag = False
itemTypes = set()
validation_dict = {'Atharva': 'ghanekar', 'Abubakar': 'siddiq', 'Shabbar': 'adamjee', 'Hussain': 'ceyloni'}


class BoardScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 600, 500)

        self.undo_flag = False
        self.data_list = []
        self.path = None
        self.mp = None
        self.previous_position = None
        self.drawing = False
        self.color = QColor("#000000")
        self.size = 1
        self.pathItem = None
        self.drawn_paths = []
        self.my_pen = None
        self.recv_timer = QTimer()
        self.recv_timer.setInterval(100)
        self.recv_timer.timeout.connect(self.build_scene_file)
        self.recv_timer.start()
        self.current_tool = None
        self.line_mode = False
        self.ellipse_mode = False
        self.rectangle_mode = False

        self.send_timer = QTimer()
        self.send_timer.setInterval(100)
        self.recv_timer.timeout.connect(self.sender_control)
        self.send_timer.start()

    def change_color(self, color):
        self.color = color

    def change_size(self, size):
        self.size = size

    def set_tool(self, tool):
        self.current_tool = tool

    def set_rectangle_mode(self, mode):
        self.rectangle_mode = mode
        self.line_mode = False
        self.ellipse_mode = False

    def set_line_mode(self, mode):
        self.line_mode = mode
        self.ellipse_mode = False
        self.rectangle_mode = False

    def set_ellipse_mode(self, mode):
        self.ellipse_mode = mode
        self.line_mode = False
        self.rectangle_mode = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.rectangle_mode:
                self.drawing = True
                self.start_pos = event.scenePos()
                self.pathItem = QGraphicsRectItem()
                self.pathItem.setPen(QPen(self.color, self.size))
                self.addItem(self.pathItem)
                print(self.items())
            elif self.line_mode:
                self.drawing = True
                self.start_pos = event.scenePos()
                self.pathItem = QGraphicsPathItem()
                self.pathItem.setPen(QPen(self.color, self.size))
                self.addItem(self.pathItem)
            elif self.ellipse_mode:
                self.drawing = True
                self.start_pos = event.scenePos()
                self.pathItem = QGraphicsEllipseItem()
                self.pathItem.setPen(QPen(self.color, self.size))
                self.addItem(self.pathItem)
            else:
                self.drawing = True
                self.path = QPainterPath()
                self.previous_position = event.scenePos()
                self.path.moveTo(self.previous_position)
                self.pathItem = QGraphicsPathItem()
                my_pen = QPen(self.color, self.size)
                my_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                self.pathItem.setPen(my_pen)
                self.addItem(self.pathItem)

            # signal_manager.call_dummy.emit()

    def mouseMoveEvent(self, event):
        if self.drawing:
            if self.rectangle_mode:
                rect = QRectF(self.start_pos, event.scenePos()).normalized()
                self.pathItem.setRect(rect)
            elif self.line_mode:
                path = QPainterPath()
                path.moveTo(self.start_pos)
                path.lineTo(event.scenePos())
                self.pathItem.setPath(path)
            elif self.ellipse_mode:
                rect = QRectF(self.start_pos, event.scenePos()).normalized()
                self.pathItem.setRect(rect)
            else:
                curr_position = event.scenePos()
                self.path.lineTo(curr_position)
                self.pathItem.setPath(self.path)
                self.previous_position = curr_position
                signal_manager.data_updated.emit(False)

            # signal_manager.function_call.emit(True)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            if self.line_mode or self.ellipse_mode or self.rectangle_mode:
                signal_manager.data_updated.emit(False)
                self.pathItem = None
            else:
                self.drawn_paths.append(self.path)
                self.pathItem = None

            global g_length
            g_length += 1
            signal_manager.data_updated.emit(False)

    def sender_control(self):
        global circular_send_buffer
        if len(circular_send_buffer) > 0:
            temp = circular_send_buffer.pop()
            print(f"Size : {len(temp)}, data : {temp}")
            signal_manager.data_sig.emit(temp, self.undo_flag)
        else:
            pass

    def scene_file(self, flag):
        global circular_send_buffer
        self.undo_flag = flag
        data = {
            'items': [],  # stores info of each line drawn
            'scene_rect': [self.width(), self.height()],  # stores dimension of scene
            'color': self.color.name(),  # store the color used
            'size': self.size,  # store the size of the pen
        }

        global g_length
        reversed_items = self.items()[::-1]  # Only take stuff that is newly added since the last time
        if g_length != 0:
            new_items = reversed_items[g_length:]
        else:
            new_items = reversed_items
        for item_index in range(len(new_items)):
            item = new_items[item_index]
            if isinstance(item, QGraphicsPathItem):
                line_data = {
                    'type': 'path',
                    'color': item.pen().color().name(),
                    'width': item.pen().widthF(),
                    'points': [(point.x(), point.y()) for subpath in item.path().toSubpathPolygons() for point in
                               subpath]  # stores the (X,Y) coordinate of the line
                }
                data['items'].append(line_data)
            elif isinstance(item, QGraphicsRectItem):
                rect_data = {
                    'type': 'rectangle',
                    'color': item.pen().color().name(),
                    'width': item.pen().widthF(),
                    'rect': [item.rect().x(), item.rect().y(), item.rect().width(), item.rect().height()]
                }
                data['items'].append(rect_data)
            elif isinstance(item, QGraphicsEllipseItem):
                ellipse_data = {
                    'type': 'ellipse',
                    'color': item.pen().color().name(),
                    'width': item.pen().widthF(),
                    'rect': [item.rect().x(), item.rect().y(), item.rect().width(), item.rect().height()]
                }
                data['items'].append(ellipse_data)

            print(f"Data is: {data}")

            # Extract points from the path
            # for subpath in item.path().toSubpathPolygons():  # to SubpathPolygons method is used to break down
            #    # the complex line into sub parts and store it
            #   line_data['points'].extend([(point.x(), point.y()) for point in subpath])

        circular_send_buffer.appendleft(data)
        # signal_manager.data_sig.emit(data, self.undo_flag)

    # def build_scene_file(self, data):
    def build_scene_file(self):
        if len(circular_recv_buffer) > 0:
            data = circular_recv_buffer.pop()
            scene_file = data['scene_info']
            # print(f"Scene: {scene_file}")

            undo_flag = data['flag']

            self.drawing = True
            prev = {'items': [],  # stores info of each line drawn
                    'scene_rect': [],  # stores dimension of scene
                    'color': "",  # store the color used
                    'size': 20  # store the size of the pen
                    }

            try:
                if 'scene_info' in data:
                    if 'scene_rect' in scene_file:
                        scene_rect = scene_file['scene_rect']
                        self.setSceneRect(0, 0, scene_rect[0], scene_rect[1])
                    else:
                        # Provide default scene rectangle if 'scene_rect' key is missing
                        self.setSceneRect(0, 0, 600, 500)  # Adjust the default values as needed
                    self.change_color(QColor(scene_file['color']))
                    self.color.setAlpha(255)

                    if 'size' in scene_file.keys():
                        self.change_size(scene_file['size'])
                        prev = scene_file
                    else:
                        pass
                    # Add lines to the scene
                    if 'items' in scene_file:
                        if scene_file['items'][0]['type'] == 'path':
                            for line_data in scene_file['items']:
                                path = QPainterPath()
                                path.moveTo(line_data['points'][0][0], line_data['points'][0][1])

                                for subpath in line_data['points'][1:]:
                                    path.lineTo(subpath[0], subpath[1])

                                pathItem = QGraphicsPathItem(path)
                                my_pen = QPen(QColor(line_data['color']), line_data['width'])
                                my_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                                pathItem.setPen(my_pen)
                                self.addItem(pathItem)

                        elif scene_file['items'][0]['type'] == 'rectangle':
                            rect_data = scene_file['items'][0]['rect']
                            rect = QRectF(rect_data[0], rect_data[1], rect_data[2], rect_data[3])
                            rectItem = QGraphicsRectItem(rect)
                            my_pen = QPen(QColor(scene_file['items'][0]['color']), scene_file['items'][0]['width'])
                            rectItem.setPen(my_pen)
                            self.addItem(rectItem)

                        elif scene_file['items'][0]['type'] == 'ellipse':
                            ellipse_data = scene_file['items'][0]['rect']
                            rect = QRectF(ellipse_data[0], ellipse_data[1], ellipse_data[2], ellipse_data[3])
                            ellipseItem = QGraphicsEllipseItem(rect)
                            my_pen = QPen(QColor(scene_file['items'][0]['color']), scene_file['items'][0]['width'])
                            ellipseItem.setPen(my_pen)
                            self.addItem(ellipseItem)
            except IndexError as e:
                print(e)
        else:
            pass

    def track_mouse_event(self, e):
        if e is True:
            self.scene_file(False)
        else:
            pass


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        ############################################################################################################
        # Ensure all buttons behave properly when clicked
        self.list_of_buttons = [self.pb_Pen, self.pb_Eraser, self.pb_Line, self.pb_Ellipse, self.pb_Rectangle]

        self.pb_Pen.setChecked(True)
        self.pb_Pen.clicked.connect(self.button_clicked)
        self.pb_Eraser.clicked.connect(self.button_clicked)
        self.pb_Line.clicked.connect(self.button_clicked)
        self.pb_Ellipse.clicked.connect(self.button_clicked)
        self.pb_Rectangle.clicked.connect(self.button_clicked)

        self.current_color = QColor("#000000")

        ############################################################################################################

        self.actionClear.triggered.connect(self.clear_canvas)
        self.actionNew.triggered.connect(self.new_file)
        self.actionClose.triggered.connect(self.close_window)
        self.actionSave_As.triggered.connect(self.save_file)
        self.actionOpen_2.triggered.connect(self.load_file)
        self.actionSave_2.triggered.connect(self.save)

        # Define what the tool buttons do
        ###########################################################################################################
        self.current_color = QColor("#000000")
        self.pb_Pen.clicked.connect(lambda e: self.color_changed(self.current_color))
        self.pb_Eraser.clicked.connect(lambda e: self.color_changed(QColor("#FFFFFF")))

        self.dial.sliderMoved.connect(self.change_size)
        self.dial.setMinimum(1)
        self.dial.setMaximum(40)
        self.dial.setWrapping(False)

        self.pb_Color.clicked.connect(self.color_dialog)
        self.pb_Undo.clicked.connect(self.undo)
        self.pb_Redo.clicked.connect(self.redo)
        self.pb_Line.clicked.connect(self.toggle_line_mode)
        self.pb_Ellipse.clicked.connect(self.toggle_ellipse_mode)
        self.pb_Rectangle.clicked.connect(self.toggle_rectangle_mode)
        ###########################################################################################################

        self.scene = BoardScene()
        self.gv_Canvas.setScene(self.scene)
        self.gv_Canvas.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        self.redo_list = []
        self.current_file = None

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Whiteboard Files (*.json)")
        if filename:
            data = {
                'items': [],
                'scene_rect': [self.scene.width(), self.scene.height()],
                'color': self.scene.color.name(),
                'size': self.scene.size
            }
            for item in reversed(self.scene.items()):
                if isinstance(item, QGraphicsPathItem):
                    line_data = {
                        'type': 'path',
                        'color': item.pen().color().name(),
                        'width': item.pen().widthF(),
                        'points': [(point.x(), point.y()) for subpath in item.path().toSubpathPolygons() for point in
                                   subpath]
                    }
                    data['items'].append(line_data)
                elif isinstance(item, QGraphicsRectItem):
                    rect_data = {
                        'type': 'rectangle',
                        'color': item.pen().color().name(),
                        'width': item.pen().widthF(),
                        'rect': [item.rect().x(), item.rect().y(), item.rect().width(), item.rect().height()]
                    }
                    data['items'].append(rect_data)
                elif isinstance(item, QGraphicsEllipseItem):
                    ellipse_data = {
                        'type': 'ellipse',
                        'color': item.pen().color().name(),
                        'width': item.pen().widthF(),
                        'rect': [item.rect().x(), item.rect().y(), item.rect().width(), item.rect().height()]
                    }
                    data['items'].append(ellipse_data)

            with open(filename, 'w') as file:
                json.dump(data, file)

    def load_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Whiteboard Files (*.json)")
        if filename:
            self.current_file = filename
            with open(filename, 'r') as file:
                data = json.load(file)

            self.scene.clear()
            self.scene.setSceneRect(0, 0, data['scene_rect'][0], data['scene_rect'][1])
            self.scene.change_color(QColor(data['color']))
            self.scene.change_size(data['size'])

            for item_data in data['items']:
                if item_data['type'] == 'path':
                    path = QPainterPath()
                    path.moveTo(item_data['points'][0][0], item_data['points'][0][1])
                    for point in item_data['points'][1:]:
                        path.lineTo(point[0], point[1])

                    pathItem = QGraphicsPathItem(path)
                    my_pen = QPen(QColor(item_data['color']), item_data['width'])
                    my_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                    pathItem.setPen(my_pen)
                    self.scene.addItem(pathItem)
                elif item_data['type'] == 'rectangle':
                    rect_data = item_data['rect']
                    rect = QRectF(rect_data[0], rect_data[1], rect_data[2], rect_data[3])
                    rectItem = QGraphicsRectItem(rect)
                    my_pen = QPen(QColor(item_data['color']), item_data['width'])
                    rectItem.setPen(my_pen)
                    self.scene.addItem(rectItem)
                elif item_data['type'] == 'ellipse':
                    ellipse_data = item_data['rect']
                    rect = QRectF(ellipse_data[0], ellipse_data[1], ellipse_data[2], ellipse_data[3])
                    ellipseItem = QGraphicsEllipseItem(rect)
                    my_pen = QPen(QColor(item_data['color']), item_data['width'])
                    ellipseItem.setPen(my_pen)
                    self.scene.addItem(ellipseItem)
            data.clear()

    def save(self):
        if self.current_file:
            data = {
                'items': [],
                'scene_rect': [self.scene.width(), self.scene.height()],
                'color': self.scene.color.name(),
                'size': self.scene.size
            }
            for item in reversed(self.scene.items()):
                if isinstance(item, QGraphicsPathItem):
                    line_data = {
                        'type': 'path',
                        'color': item.pen().color().name(),
                        'width': item.pen().widthF(),
                        'points': [(point.x(), point.y()) for subpath in item.path().toSubpathPolygons() for point in
                                   subpath]
                    }
                    data['items'].append(line_data)
                elif isinstance(item, QGraphicsRectItem):
                    rect_data = {
                        'type': 'rectangle',
                        'color': item.pen().color().name(),
                        'width': item.pen().widthF(),
                        'rect': [item.rect().x(), item.rect().y(), item.rect().width(), item.rect().height()]
                    }
                    data['items'].append(rect_data)
                elif isinstance(item, QGraphicsEllipseItem):
                    ellipse_data = {
                        'type': 'ellipse',
                        'color': item.pen().color().name(),
                        'width': item.pen().widthF(),
                        'rect': [item.rect().x(), item.rect().y(), item.rect().width(), item.rect().height()]
                    }
                    data['items'].append(ellipse_data)

            with open(self.current_file, 'w') as file:
                json.dump(data, file)
        else:
            self.save_file()

    def close_window(self):
        self.close()

    def new_file(self):
        new_file = MainWindow()
        new_file.show()

    def change_size(self):
        self.scene.change_size(self.dial.value())

    def undo(self):
        if self.scene.items():
            latest_item = self.scene.items()
            self.redo_list.append(latest_item)
            self.scene.removeItem(latest_item[0])
            signal_manager.function_call.emit(True)

    def redo(self):
        if self.redo_list:
            item = self.redo_list.pop(-1)
            self.scene.addItem(item[0])
            signal_manager.function_call.emit(True)

    def clear_canvas(self):
        self.scene.clear()

    def color_dialog(self):
        color_dialog = QColorDialog()
        color_dialog.show()
        color_dialog.currentColorChanged.connect(lambda e: self.color_dialog_color_changed(color_dialog.currentColor()))
        self.current_color = color_dialog.currentColor()

    def color_dialog_color_changed(self, current_color):
        self.color_changed(current_color)
        if self.pb_Eraser.isChecked():
            self.pb_Eraser.setChecked(False)
            self.pb_Pen.setChecked(True)
        elif self.pb_Pen.isChecked():
            self.current_color = current_color

    def deselect_current_mode(self):
        self.scene.line_mode = False
        self.scene.ellipse_mode = False
        self.scene.rectangle_mode = False
        self.pb_Line.setChecked(False)
        self.pb_Ellipse.setChecked(False)
        self.pb_Rectangle.setChecked(False)

    def color_changed(self, color):
        self.scene.change_color(color)
        # self.scene.scene_file()
        # self.scene_file()
        # self.erase_path(self.scene.drawn_paths)

    def button_clicked(self):
        self.deselect_current_mode()

        sender_button = self.sender()
        for btn in self.list_of_buttons:
            if btn is not sender_button:
                btn.setChecked(False)

    def toggle_line_mode(self):
        self.deselect_current_mode()
        self.scene.set_line_mode(True)
        self.pb_Line.setChecked(True)
        self.scene.set_tool("Line")

    def toggle_ellipse_mode(self):
        self.deselect_current_mode()
        self.scene.set_ellipse_mode(True)
        self.pb_Ellipse.setChecked(True)
        self.scene.set_tool("Ellipse")

    def toggle_rectangle_mode(self):
        self.deselect_current_mode()
        self.scene.set_rectangle_mode(True)
        self.pb_Rectangle.setChecked(True)
        self.scene.set_tool("Rectangle")


def update_data(data_recv: dict):
    global circular_recv_buffer
    global buffer_flag
    circular_recv_buffer.appendleft(data_recv)
    # print(circular_recv_buffer)
    buffer_flag = 1


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")

        # Setting window size
        self.setFixedSize(450, 275)

        # Setting the gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(135, 206, 235))  # Light blue color at the top
        gradient.setColorAt(1.0, QColor(65, 105, 225))  # Royal blue color at the bottom

        # Set the gradient as the background
        palette = self.palette()
        palette.setBrush(QPalette.Window, gradient)
        self.setPalette(palette)

        layout = QVBoxLayout()

        # Username Section
        self.username_input = QLineEdit()
        self.username_input.setFixedHeight(50)
        self.username_input.setPlaceholderText("Username")  # Set placeholder text for username input box
        self.username_input.setFont(QFont("Arial", 12))  # Set custom font for the input text
        self.username_input.setStyleSheet(
            "QLineEdit { padding: 10px 20px; margin-left: 30px; margin-right: 30px;}")  # Set margin and padding
        layout.addWidget(self.username_input)

        # Password Section
        self.password_input = QLineEdit()
        self.password_input.setFixedHeight(50)
        self.password_input.setPlaceholderText("Password")  # Set placeholder text for password input box
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)  # Setting to password mode to display dots
        self.password_input.setFont(QFont("Arial", 12))  # Set custom font for the input text
        self.password_input.setStyleSheet(
            "QLineEdit { padding: 10px 20px; margin-left: 30px; margin-right: 30px;}")  # Set margin and padding
        layout.addWidget(self.password_input)

        # Login Button
        self.login_button = QPushButton("LOGIN")
        self.login_button.setFixedHeight(50)
        self.login_button.clicked.connect(self.login)  # Connecting it to login function
        self.login_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; padding: 10px 20px; font-size: 20px; margin-left: 30px; margin-right: 30px; font-weight: bold;}")  # Styling the button
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        print("Username:", username)
        print("Password:", password)
        self.close()


def validate_credentials(username: str, pwd: str):
    global validation_dict
    global login_flag
    if username in validation_dict.keys():
        if pwd == validation_dict[username]:
            print("login successful")
            login_flag = True
        else:
            print("unsuccessful")
            login_flag = False
    else:
        print("invalid username")
        login_flag = False
    print(login_flag)


def init_gui():
    app = QApplication()
    window = MainWindow()

    # Start the ping_server thread
    # ping_server_thread = threading.Thread(target=run_ping_server, args=(client,))
    # ping_server_thread.start()
    #
    # # Start the build_scene thread
    # build_scene_thread = threading.Thread(target=run_build_scene, args=(window,))
    # build_scene_thread.start()
    log = LoginWindow()
    log.show()
    app.exec()

    signal_manager.function_call.connect(window.scene.track_mouse_event)
    signal_manager.data_updated.connect(window.scene.scene_file)
    # signal_manager.data_ack.connect(window.scene.build_scene_file)
    signal_manager.data_ack.connect(update_data)

    signal_manager.send_info2.connect(validate_credentials)
    signal_manager.function_call.connect(window.scene.track_mouse_event)
    signal_manager.data_updated.connect(window.scene.scene_file)
    signal_manager.data_ack.connect(window.scene.build_scene_file)

    username = log.username_input.text()
    pwd = log.password_input.text()
    signal_manager.send_info2.emit(username, pwd)

    if login_flag:
        client = MyClient()
        start_client(client)
        signal_manager.data_sig.connect(client.ping_server)
        window.show()
        app.exec()
    else:
        sys.exit()


if __name__ == '__main__':
    init_gui()
