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
    QPointF
)
import json
from WhiteboardApplication.UI.board import Ui_MainWindow
from tcpServerNet import start_server, MyServer, signal_manager

itemTypes = set()
myserver = MyServer()


class User:
    def __init__(self):
        pass


class BoardScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 600, 500)
        self.flag = 0
        self.next_z_index = 0

        self.temppath = []
        self.path = None
        self.previous_position = None
        self.drawing = False
        self.color = QColor("#000000")
        self.size = 1
        self.pathItem = None
        self.drawn_paths = []
        self.my_pen = None
        self.data = {"event": "",
                     "state": False,
                     "position": None,
                     "color": None,
                     "widthF": None,
                     "width": None,
                     "capStyle": None,
                     "joinStyle": None,
                     "style": None,
                     "pattern": None,
                     "patternOffset": None
                     }

        self.default_z_index = 0  # Set a default z-index
        self.eraser_z_index = None  # Store eraser's z-index

    def get_topmost_z_index(self):
        highest_z = float("-inf")
        for item in self.items():
            highest_z = max(highest_z, item.zValue())
        return highest_z

    def set_eraser_z_index(self, z_index):
        self.eraser_z_index = z_index
        for item in self.items():
            if isinstance(item, QGraphicsPathItem):
                if item.pen().color() == Qt.white:
                    item.setZValue(self.eraser_z_index)

    def set_default_z_index(self):
        for item in self.items():
            if isinstance(item, QGraphicsPathItem):
                if item.pen().color() != Qt.white:
                    item.setZValue(self.default_z_index)

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

            # print(self.items())
            for item in self.items():
                itemTypes.add(type(item).__name__)

            # print(itemTypes)
            self.drawing_events("mousePressEvent")

            # print(self.data)
            # itemTypes.clear()
            signal_manager.function_call.emit(True)

    def mouseMoveEvent(self, event):
        if self.drawing:
            curr_position = event.scenePos()
            self.path.lineTo(curr_position)
            self.pathItem.setPath(self.path)
            self.previous_position = curr_position
            # print(self.pathItem)
            # print(self.items())

            for item in self.items():
                itemTypes.add(type(item).__name__)

            self.drawing_events("mouseMoveEvent")
            # print(self.data)

            # print(itemTypes)
            # itemTypes.clear()
            signal_manager.function_call.emit(True)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.previous_position = None
            self.drawing = False
            # Save the drawn path
            self.drawn_paths.append(self.path)

            for item in self.items():
                itemTypes.add(type(item).__name__)

            self.drawing_events("mouseReleaseEvent")
            signal_manager.function_call.emit(True)

    def get_drawn_paths(self):
        return self.drawn_paths

    def clear_drawn_paths(self):
        self.drawn_paths = []
        self.clear()

    def drawing_events(self, event_name: str):
        self.data["state"] = self.drawing
        self.data["event"] = event_name
        self.data["position"] = self.previous_position
        self.data["color"] = self.my_pen.color()
        self.data["widthF"] = self.my_pen.widthF()
        self.data["width"] = self.my_pen.width()
        self.data["capStyle"] = self.my_pen.capStyle()
        self.data["joinStyle"] = self.my_pen.joinStyle()
        self.data["style"] = self.my_pen.style()
        self.data["pattern"] = self.my_pen.dashPattern()
        self.data["patternOffset"] = self.my_pen.dashOffset()

    def configure_pen(self, scene_info):
        color = QColor(scene_info["color"])
        size = scene_info["width"]
        style = getattr(Qt.PenStyle, scene_info["style"])
        pattern = scene_info["pattern"]

        self.my_pen = QPen(color, size)
        self.my_pen.setStyle(style)
        self.my_pen.setDashPattern(pattern)
        self.pathItem.setPen(self.my_pen)

    def get_drawing_events(self, scene_info):
        prev = None
        point = QPointF(scene_info["position"][0], scene_info["position"][1])
        reconstructed_path = scene_info["path"]

        if scene_info["event"] == "mousePressEvent":
            if not self.drawing:
                self.path = QPainterPath()
                self.pathItem = QGraphicsPathItem()
                self.configure_pen(scene_info)
                self.pathItem.setPen(self.my_pen)
                self.pathItem.setPath(self.path)
                self.addItem(self.pathItem)
                self.drawing = True
                prev = point
                self.flag = 1

        elif scene_info["event"] == "mouseMoveEvent":
            color = QColor(scene_info["color"])
            size = scene_info["width"]
            pattern = scene_info["pattern"]

            style = getattr(Qt.PenStyle, scene_info["style"])
            if self.drawing and self.flag == 0:
                self.configure_pen(scene_info)
                self.pathItem.setPen(self.my_pen)
                self.pathItem.setPath(self.path)
                self.addItem(self.pathItem)

            elif self.flag == 1:
                self.my_pen = QPen(color, size)
                self.my_pen.setStyle(style)
                self.my_pen.setDashPattern(scene_info["pattern"])
                self.path.moveTo(self.path.currentPosition())
                self.path.lineTo(point)
                self.pathItem.setPen(self.my_pen)
                self.pathItem.setPath(self.path)
                self.addItem(self.pathItem)

        elif scene_info["event"] == "mouseReleaseEvent":
            self.drawing = False
            self.my_pen = None
            self.path = None
            # print(f"Moved to point : {point}")

            # self.removeItem(self.pathItem)
            self.pathItem = None
            self.flag = 1

    def get_z_index_range(self):
        highest_z = float("-inf")
        lowest_z = float("inf")
        for item in self.items():
            highest_z = max(highest_z, item.zValue())
            lowest_z = min(lowest_z, item.zValue())
        return highest_z, lowest_z


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
        self.actionCoolDude.triggered.connect(self.New_file)
        self.actionClose_2.triggered.connect(self.Close_window)
        self.actionSave_As.triggered.connect(self.save_file)
        self.actionNew_3.triggered.connect(self.load_file)

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
            for item in reversed(self.scene.items()):
                if isinstance(item, QGraphicsPathItem):
                    line_data = {
                        'color': item.pen().color().name(),
                        'width': item.pen().widthF(),
                        'points': [],  # stores the (X,Y) coordinate of the line
                        # 'z_value': item.zValue()  # Store the z-value
                    }
                    # print(f"Item value : {item.zValue()}")

                    # Extract points from the path
                    for subpath in item.path().toSubpathPolygons():  # to SubpathPolygons method is used to break down
                        # the complex line into sub parts and store it
                        line_data['points'].extend([(point.x(), point.y()) for point in subpath])

                    data['lines'].append(line_data)

            with open(filename, 'w') as file:
                json.dump(data, file)

    def load_file(self):
        self.scene.z_index_counter = 0
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

            z_index_counter = 0

            items = []  # List to hold items before sorting
            # Add lines to the scene
            for line_data in data['lines']:
                path = QPainterPath()
                path.moveTo(line_data['points'][0][0], line_data['points'][0][1])

                for subpath in line_data['points'][1:]:
                    path.lineTo(subpath[0], subpath[1])

                pathItem = QGraphicsPathItem(path)
                pathItem.setZValue(z_index_counter)  # Assign unique z-index
                z_index_counter += 1  # Increment counter
                my_pen = QPen(QColor(line_data['color']), line_data['width'])
                my_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pathItem.setPen(my_pen)

                # items.append(pathItem)

                self.scene.addItem(pathItem)
            #
            # items.sort(key=lambda x: x.zValue())
            # for item in items:
                # self.scene.addItem(pathItem)

    def Close_window(self):
        self.close()

    def New_file(self):
        new_file = MainWindow()
        new_file.show()

    def change_size(self):
        self.scene.change_size(self.dial.value())

    def undo(self):
        if self.scene.items():
            print('Undo called')
            print(self.scene.items())
            latest_item = self.scene.items()
            self.redo_list.append(latest_item)
            self.scene.removeItem(latest_item[0])

    def redo(self):
        if self.redo_list:
            item = self.redo_list.pop(-1)
            self.scene.addItem(item[0])

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

    def button_clicked(self):
        sender_button = self.sender()
        for btn in self.list_of_buttons:
            if btn is not sender_button:
                btn.setChecked(False)

    def build_scene_file(self, data):
        self.scene.clear()
        scene_file = data['scene_info']

        undo_flag = data['flag']

        self.scene.drawing = True
        prev = {'lines': [],  # stores info of each line drawn
                'scene_rect': [],  # stores dimension of scene
                'color': "",  # store the color used
                'size': 20  # store the size of the pen
                }

        top_z = self.scene.get_topmost_z_index()
        try:
            if 'scene_info' in data:
                if 'scene_rect' in scene_file:
                    scene_rect = scene_file['scene_rect']
                    self.scene.setSceneRect(0, 0, scene_rect[0], scene_rect[1])
                else:
                    # Provide default scene rectangle if 'scene_rect' key is missing
                    self.scene.setSceneRect(0, 0, 600, 500)  # Adjust the default values as needed
                self.scene.change_color(QColor(scene_file['color']))
                self.scene.color.setAlpha(255)

                if 'size' in scene_file.keys():
                    self.scene.change_size(scene_file['size'])
                    prev = scene_file
                else:
                    pass
                # Add lines to the scene
                if 'lines' in scene_file:
                    for line_data in scene_file['lines']:
                        path = QPainterPath()
                        path.moveTo(line_data['points'][0][0], line_data['points'][0][1])
                        print("line_data is cool")

                        for subpath in line_data['points'][1:]:
                            path.lineTo(subpath[0], subpath[1])
                        print("Whatever tf subpath is, it's cool")

                        self.scene.temppath.clear()

                        if path not in self.scene.temppath:
                            self.scene.temppath.append(path)
                        print(3)
                        pathItem = QGraphicsPathItem(path)
                        self.scene.next_z_index += 10  # Adjust increment as needed
                        pathItem.setZValue(self.scene.next_z_index)
                        my_pen = QPen(QColor(line_data['color']), line_data['width'])
                        my_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                        pathItem.setPen(my_pen)
                        pathItem.setZValue(self.scene.itemsBoundingRect().height() + 1)
                        self.scene.addItem(pathItem)

        except IndexError as e:
            print(e)
            pass


if __name__ == '__main__':
    app = QApplication()
    start_server(myserver)
    window = MainWindow()
    signal_manager.action_signal.connect(window.scene.get_drawing_events)
    signal_manager.data_ack.connect(window.build_scene_file)
    window.show()

    app.exec()
