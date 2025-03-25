import sys
import cProfile, pstats
from math import atan2, degrees, sin, cos, pi

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
    QGraphicsItem,
    QGraphicsEllipseItem,
    QGraphicsRectItem,
    QGraphicsView,
)

from PySide6.QtGui import (
    QPen,
    Qt,
    QPainter,
    QPainterPath,
    QColor,
    QPalette,
    QLinearGradient,
    QFont,
)

from PySide6.QtCore import (
    Qt,
    QObject,
    Signal,
    Slot,
    QTimer,
    QRectF,
    QThread,
    QPointF,
)
import json
from TcpClientNet import start_client, MyClient, signal_manager
from Scene import *
from WhiteboardApplication.UI.board import Ui_MainWindow
from collections import deque


itemTypes = set()
circular_recv_buffer = deque(maxlen=20)
circular_send_buffer = deque(maxlen=20)
buffer_flag = 0
login_flag = False
itemTypes = set()
validation_dict = {'Atharva': 'ghanekar', 'Abubakar': 'siddiq', 'Shabbar': 'adamjee', 'Hussain': 'ceyloni', '': ''}


class PanningGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__()

        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setBackgroundBrush(QColor("white"))
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.panning = False
        self.last_pos = QPointF()

        # Disable scrollbars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning = True
            self.last_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.panning:
            delta = self.mapToScene(event.pos()) - self.mapToScene(self.last_pos)
            self.last_pos = event.pos()

            # Move the scene by the delta amount
            self.setSceneRect(self.sceneRect().translated(-delta.x(), -delta.y()))
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event, /):
        scroll_delta = event.angleDelta()
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            zoom_factor = 1.1 if scroll_delta.y() > 0 else 0.9
            self.scale(zoom_factor, zoom_factor)
        else:
            if scroll_delta.y() != 0 or scroll_delta.x() != 0:
                pan_y = -scroll_delta.y() * 0.5
                pan_x = -scroll_delta.x() * 0.5
                self.setSceneRect(self.sceneRect().translated(pan_x, pan_y))


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, client):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("SynqBoard")
        self.client = client

        # Initialize Voice Client
        self.voice_client = self.client.voice_client
        ############################################################################################################
        # Ensure all buttons behave properly when clicked
        self.list_of_buttons = [self.pb_Pen, self.pb_Eraser, self.pb_Line, self.pb_Ellipse, self.pb_Rectangle]

        self.pb_Pen.setChecked(True)
        self.pb_Pen.clicked.connect(self.button_clicked)
        self.pb_Eraser.clicked.connect(self.button_clicked)
        self.pb_Line.clicked.connect(self.button_clicked)
        self.pb_Ellipse.clicked.connect(self.button_clicked)
        self.pb_Rectangle.clicked.connect(self.button_clicked)
        self.pb_Select.clicked.connect(self.button_clicked)

        # Connect Mic Button to toggle function
        self.pb_Mic.clicked.connect(self.toggle_mic)


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
        #self.pb_Eraser.clicked.connect(lambda e: self.color_changed(QColor("#FFFFFF")))

        self.dial.sliderMoved.connect(self.change_size)
        self.dial.setMinimum(1)
        self.dial.setMaximum(40)
        self.dial.setWrapping(False)

        self.pb_Color.clicked.connect(self.color_dialog)
        self.pb_Undo.clicked.connect(self.undo)
        self.pb_Redo.clicked.connect(self.redo)
        self.pb_Pen.clicked.connect(self.toggle_pen_mode)
        self.pb_Line.clicked.connect(self.toggle_line_mode)
        self.pb_Ellipse.clicked.connect(self.toggle_ellipse_mode)
        self.pb_Rectangle.clicked.connect(self.toggle_rectangle_mode)
        ###########################################################################################################

        old_view = self.gv_Canvas
        self.gv_Canvas = PanningGraphicsView(self.centralwidget)
        self.gv_Canvas.setObjectName("gv_Canvas")
        self.gridLayout.replaceWidget(old_view, self.gv_Canvas)
        old_view.deleteLater()

        self.scene = BoardScene()
        self.gv_Canvas.setScene(self.scene)
        self.gv_Canvas.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.resize_scene()

        self.cb_Fill_Color.stateChanged.connect(self.scene.toggle_fill_color)

        self.redo_list = []
        self.current_file = None

    def toggle_mic(self):
        """Toggle microphone ON/OFF."""
        self.voice_client.toggle_mic()
        self.pb_Mic.setText("Mic ON" if self.voice_client.mic_on else "Mic OFF")

    def showEvent(self, event, /):
        self.resize_scene()
        super().showEvent(event)

    def resizeEvent(self, event):
        self.resize_scene()
        super().resizeEvent(event)

    def resize_scene(self):
        rect = self.gv_Canvas.viewport().rect()
        self.scene.setSceneRect(0, 0, rect.width(), rect.height())

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
        if self.scene.stroke_groups:
            latest_group = self.scene.stroke_groups.pop()
            self.redo_list.append(latest_group)

            for item in latest_group:
                self.scene.removeItem(item)

    def redo(self):
        if self.redo_list:
            group = self.redo_list.pop()
            for item in group:
                self.scene.addItem(item)
                self.scene.stroke_groups.append(group)

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
        self.pb_Select.setChecked(False)

    def color_changed(self, color):
        self.scene.change_color(color)

    def button_clicked(self):
        self.deselect_current_mode()

        sender_button = self.sender()
        for btn in self.list_of_buttons:
            if btn is not sender_button:
                btn.setChecked(False)

        if sender_button == self.pb_Eraser:
            self.scene.set_eraser_mode(True)
        elif sender_button == self.pb_Select:
            self.scene.set_selection_mode(True)

    def toggle_select_mode(self):
        self.deselect_current_mode()
        self.scene.set_selection_mode(True)
        self.pb_Select.setChecked(True)

    def toggle_pen_mode(self):
        self.deselect_current_mode()
        self.scene.set_pen_mode(True)
        self.pb_Pen.setChecked(True)

    def toggle_line_mode(self):
        self.deselect_current_mode()
        self.scene.set_line_mode(True)
        self.pb_Line.setChecked(True)

    def toggle_ellipse_mode(self):
        self.deselect_current_mode()
        self.scene.set_ellipse_mode(True)
        self.pb_Ellipse.setChecked(True)

    def toggle_rectangle_mode(self):
        self.deselect_current_mode()
        self.scene.set_rectangle_mode(True)
        self.pb_Rectangle.setChecked(True)

    def closeEvent(self, event):
        self.scene.cleanup_threads()
        self.client.cleanup_threads()
        super().closeEvent(event)


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


def init_gui():
    app = QApplication()

    log = LoginWindow()
    log.show()
    app.exec()

    signal_manager.send_info.connect(validate_credentials)

    username = log.username_input.text()
    pwd = log.password_input.text()
    signal_manager.send_info.emit(username, pwd)

    if login_flag:
        client = MyClient()
        start_client(client)
        signal_manager.data_serialized.connect(client.send_data)
        window = MainWindow(client)
        signal_manager.data_updated.connect(window.scene.scene_file)
        signal_manager.data_ack.connect(window.scene.build_scene_file)
        window.show()
        app.exec()
    else:
        sys.exit()


if __name__ == '__main__':
    with cProfile.Profile() as profile:
        init_gui()

    results = pstats.Stats(profile)
    results.sort_stats(pstats.SortKey.TIME)
    results.print_stats()