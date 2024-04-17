from PySide6.QtWidgets import (
    QMainWindow,
    QGraphicsScene,
    QApplication,
    QGraphicsPathItem,
    QColorDialog,
    QFileDialog
)

from PySide6.QtGui import (
    QPen,
    Qt,
    QPainter,
    QPainterPath,
    QColor,
)

from PySide6.QtCore import (
    Qt,
)
import json
from TcpClientNet import start_client, MyClient, signal_manager
from WhiteboardApplication.UI.board import Ui_MainWindow

itemTypes = set()

g_length = 0


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

    def change_color(self, color):
        self.color = color

    def change_size(self, size):
        self.size = size

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.path = QPainterPath()
            self.previous_position = event.scenePos()
            self.path.moveTo(self.previous_position)
            self.pathItem = QGraphicsPathItem()
            self.my_pen = QPen(self.color, self.size)
            self.my_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            self.pathItem.setPen(self.my_pen)
            self.addItem(self.pathItem)

            # signal_manager.function_call.emit(True)

    def mouseMoveEvent(self, event):
        if self.drawing:
            curr_position = event.scenePos()
            self.path.lineTo(curr_position)
            self.pathItem.setPath(self.path)
            self.previous_position = curr_position
            signal_manager.function_call.emit(True)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.previous_position = None
            self.drawing = False

            # signal_manager.function_call.emit(True)
            global g_length
            g_length += 1

    def scene_file(self, flag):
        self.undo_flag = flag
        data = {
            'lines': [],  # stores info of each line drawn
            'scene_rect': [self.width(), self.height()],  # stores dimension of scene
            'color': self.color.name(),  # store the color used
            'size': self.size,  # store the size of the pen
            'next_size': 0,
        }

        self.data_list.append(data)

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
                    'color': item.pen().color().name(),
                    'width': item.pen().widthF(),
                    'points': []  # stores the (X,Y) coordinate of the line
                }

                # Extract points from the path
                for subpath in item.path().toSubpathPolygons():  # to SubpathPolygons method is used to break down
                    # the complex line into sub parts and store it
                    line_data['points'].extend([(point.x(), point.y()) for point in subpath])

                data['lines'].append(line_data)
        if len(self.data_list) > 1:
            self.data_list[0]['next_size'] = self.data_list[1].__sizeof__()
            signal_manager.data_sig.emit(self.data_list.pop(0), self.undo_flag)

    def build_scene_file(self, data):
        scene_file = data['scene_info']

        undo_flag = data['flag']

        self.drawing = True
        prev = {'lines': [],  # stores info of each line drawn
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
                if 'lines' in scene_file:
                    for line_data in scene_file['lines']:
                        path = QPainterPath()
                        path.moveTo(line_data['points'][0][0], line_data['points'][0][1])

                        for subpath in line_data['points'][1:]:
                            path.lineTo(subpath[0], subpath[1])

                        pathItem = QGraphicsPathItem(path)
                        my_pen = QPen(QColor(line_data['color']), line_data['width'])
                        my_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                        pathItem.setPen(my_pen)
                        pathItem.setZValue(self.itemsBoundingRect().height() + 1)
                        self.addItem(pathItem)
        except IndexError as e:
            print(e)

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
        self.list_of_buttons = [self.pb_Pen, self.pb_Eraser]

        self.pb_Pen.setChecked(True)
        self.pb_Pen.clicked.connect(self.button_clicked)
        self.pb_Eraser.clicked.connect(self.button_clicked)

        self.current_color = QColor("#000000")

        ############################################################################################################

        self.actionClear.triggered.connect(self.clear_canvas)
        self.actionNew.triggered.connect(self.new_file)
        self.actionClose.triggered.connect(self.close_window)
        self.actionSave_As.triggered.connect(self.save_file)
        self.actionOpen.triggered.connect(self.load_file)

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
        ###########################################################################################################

        self.scene = BoardScene()
        self.gv_Canvas.setScene(self.scene)
        self.gv_Canvas.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        self.redo_list = []

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Whiteboard Files (*.json)")  # open dialog
        # window to save file
        if filename:
            data = {
                'lines': [],  # stores info of each line drawn
                'scene_rect': [self.scene.width(), self.scene.height()],  # stores dimension of scene
                'color': self.scene.color.name(),  # store the color used
                'size': self.scene.size  # store the size of the pen
            }
            # loop for checking of drawn path
            for item in self.scene.items():
                if isinstance(item, QGraphicsPathItem):
                    line_data = {
                        'color': item.pen().color().name(),
                        'width': item.pen().widthF(),
                        'points': []  # stores the (X,Y) coordinate of the line
                    }

                    # Extract points from the path
                    for subpath in item.path().toSubpathPolygons():  # to SubpathPolygons method is used to break down
                        # the complex line into sub parts and store it
                        line_data['points'].extend([(point.x(), point.y()) for point in subpath])

                    data['lines'].append(line_data)

            with open(filename, 'w') as file:
                json.dump(data, file)

    def load_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Whiteboard Files (*.json)")  # open dialog
        # window to Open the file
        if filename:  # reading the file
            with open(filename, 'r') as file:
                data = json.load(file)

            self.scene.clear()

            # Set scene properties
            self.scene.setSceneRect(0, 0, data['scene_rect'][0], data['scene_rect'][1])
            self.scene.change_color(QColor(data['color']))
            self.scene.change_size(data['size'])

            # Add lines to the scene
            for line_data in data['lines']:
                path = QPainterPath()
                path.moveTo(line_data['points'][0][0], line_data['points'][0][1])

                for subpath in line_data['points'][1:]:
                    path.lineTo(subpath[0], subpath[1])

                pathItem = QGraphicsPathItem(path)
                my_pen = QPen(QColor(line_data['color']), line_data['width'])
                my_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pathItem.setPen(my_pen)

                self.scene.addItem(pathItem)

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

    def color_changed(self, color):
        self.scene.change_color(color)
        # self.scene.scene_file()
        # self.scene_file()
        # self.erase_path(self.scene.drawn_paths)

    def button_clicked(self):
        sender_button = self.sender()
        for btn in self.list_of_buttons:
            if btn is not sender_button:
                btn.setChecked(False)


def init_gui():
    app = QApplication()
    window = MainWindow()

    client = MyClient()
    start_client(client)

    signal_manager.data_sig.connect(client.ping_server)
    signal_manager.function_call.connect(window.scene.track_mouse_event)
    signal_manager.data_updated.connect(window.scene.scene_file)
    signal_manager.data_ack.connect(window.scene.build_scene_file)

    window.show()
    app.exec()


if __name__ == '__main__':
    init_gui()
