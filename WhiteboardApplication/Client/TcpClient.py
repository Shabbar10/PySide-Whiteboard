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
    QPicture,
    QPixmap
)

from PySide6.QtCore import (
    Qt,
    QIODevice,
    QFile,
    QDataStream,
    QPointF,
    QObject,
    Signal
)
import json
from client_mg import SignalManager
from TcpClientNet import start_client, MyClient
from TcpClientNet import UdpSock
from WhiteboardApplication.UI.board import Ui_MainWindow

itemTypes = set()

signal_manager = SignalManager()


class User:
    def __init__(self):
        pass


class BoardScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 600, 500)

        self.path = None
        self.mp = None
        # self.mp = None
        self.previous_position = None
        self.drawing = False
        self.color = QColor("#000000")
        self.size = 1
        self.pathItem = None
        self.drawn_paths = []
        self.my_pen = None
        self.data = {"event": "",
                     "state": False,
                     "path": None,
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
        self.pos = []
        self.jsonpath = None
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
            self.pos.clear()
            self.drawing = True
            self.path = QPainterPath()
            self.previous_position = event.scenePos()
            self.path.moveTo(self.previous_position)
            self.pathItem = QGraphicsPathItem()
            self.my_pen = QPen(self.color, self.size)
            self.my_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            self.pathItem.setPen(self.my_pen)
            self.addItem(self.pathItem)

            self.pos.append(self.previous_position.y())
            self.pos.append(self.previous_position.x())
            # self.pos.clear()

            # print(self.items())
            for item in self.items():
                itemTypes.add(type(item).__name__)

            # print(itemTypes)
            self.drawing_events("mousePressEvent")
            # self.send_updates()

            # print(f"Path original: {self.path}")
            # self.jsonpath = self.serialize_path(self.path)
            #
            # new = self.deserialize_path(jsonpath)

            # print(f"JSON : {new}")

            # print(self.data)
            # itemTypes.clear()
            signal_manager.function_call.emit(True)

    def serialize_path(self, path):
        elements = []
        for i in range(path.elementCount()):
            element_type = path.elementAt(i).type
            if element_type == QPainterPath.MoveToElement:
                elements.append(('moveTo', (path.elementAt(i).x, path.elementAt(i).y)))
            elif element_type == QPainterPath.LineToElement:
                elements.append(('lineTo', (path.elementAt(i).x, path.elementAt(i).y)))
            # Add more cases for other types like CubicToElement, etc.
        return json.dumps(elements)

    def deserialize_path(self, serialized_data):
        path = QPainterPath()
        elements = json.loads(serialized_data)
        for element in elements:
            if element[0] == 'moveTo':
                path.moveTo(*element[1])
            elif element[0] == 'lineTo':
                path.lineTo(*element[1])
            # Add more cases for other types like CubicToElement, etc.
        return path

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.pos.clear()

            curr_position = event.scenePos()
            self.path.lineTo(curr_position)
            self.pathItem.setPath(self.path)
            self.previous_position = curr_position
            # print(self.pathItem)
            # print(self.items())
            self.pos.append(self.previous_position.y())
            self.pos.append(self.previous_position.x())

            # self.pos.clear()
            for item in self.items():
                itemTypes.add(type(item).__name__)

                # if event.button() == Qt.MouseButton.LeftButton:
                self.drawing_events("mouseMoveEvent")
                # print(event.buttons())
            # else:
            #     self.drawing_events("mouseReleaseEvent")

            # print(self.path)

            # self.send_updates()
            # print(f"Path original: {self.path}")
            self.jsonpath = self.serialize_path(self.path)
            # new = self.deserialize_path(jsonpath)

            # print(f"JSON : {new}")

            # print(self.data)

            # print(itemTypes)
            # itemTypes.clear()

            signal_manager.function_call.emit(True)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.pos.clear()
            if self.previous_position:
                self.pos.append(self.previous_position.y())
                self.pos.append(self.previous_position.x())
            self.previous_position = None
            self.drawing = False
            # Save the drawn path
            self.drawn_paths.append(self.path)
            # print(self.pathItem)
            # print(self.items())

            # self.pos.clear()

            for item in self.items():
                itemTypes.add(type(item).__name__)

            # print(itemTypes)
            # itemTypes.clear()
            self.drawing_events("mouseReleaseEvent")

            # self.scene_file()
            # self.send_updates()
            # print(self.data)
            # print(self.path)

            # print(f"Path original: {self.path}")

            self.jsonpath = self.serialize_path(self.path)
            # new = self.deserialize_path(jsonpath)
            # print(f"JSON : {new}")
            signal_manager.function_call.emit(True)

    def send_updates(self):
        if self.drawing:
            data_to_send = self.data
            # print(data_to_send)
            # self.drawing_events()
            print("Reached into sending updates")
            # signal_manager.send_info.emit(data_to_send)
            data_to_send.clear()
        else:
            pass

    def get_drawn_paths(self):
        return self.drawn_paths

    def clear_drawn_paths(self):
        self.drawn_paths = []
        self.clear()

    def pen_cap_style_to_string(self, cap_style) -> str:
        # Convert PenCapStyle to string representation
        if cap_style == Qt.PenCapStyle.FlatCap:
            return "FlatCap"
        elif cap_style == Qt.PenCapStyle.SquareCap:
            return "SquareCap"
        elif cap_style == Qt.PenCapStyle.RoundCap:
            return "RoundCap"
        else:
            return "FlatCap"  # Default to something

    def pen_join_style_to_string(self, join_style):
        # Convert PenJoinStyle to string representation
        if join_style == Qt.PenJoinStyle.MiterJoin:
            return "MiterJoin"
        elif join_style == Qt.PenJoinStyle.BevelJoin:
            return "BevelJoin"
        elif join_style == Qt.PenJoinStyle.RoundJoin:
            return "RoundJoin"
        else:
            return "UnknownJoin"

        ############################################################################################################

    # PenCapStyle
    def pen_style_to_string(self, pen_style):
        # Convert PenStyle to string representation
        if pen_style == Qt.PenStyle.NoPen:
            return "NoPen"
        elif pen_style == Qt.PenStyle.SolidLine:
            return "SolidLine"
        elif pen_style == Qt.PenStyle.DashLine:
            return "DashLine"
        elif pen_style == Qt.PenStyle.DotLine:
            return "DotLine"
        elif pen_style == Qt.PenStyle.DashDotLine:
            return "DashDotLine"
        elif pen_style == Qt.PenStyle.DashDotDotLine:
            return "DashDotDotLine"
        elif pen_style == Qt.PenStyle.CustomDashLine:
            return "CustomDashLine"
        else:
            return "UnknownPenStyle"

    def drawing_events(self, event_name: str):
        if len(self.pos) >= 2:
            color = self.my_pen.color().name()
            cp_style = self.pen_cap_style_to_string(self.my_pen.capStyle())
            join_style = self.pen_join_style_to_string(self.my_pen.joinStyle())
            style = self.pen_style_to_string(self.my_pen.style())
            position = (self.pos[1], self.pos[0])

            self.data["path"] = self.jsonpath
            self.data["state"] = self.drawing
            self.data["event"] = event_name
            self.data["position"] = position
            self.data["color"] = color
            self.data["widthF"] = self.my_pen.widthF()
            self.data["width"] = self.my_pen.width()
            self.data["capStyle"] = cp_style
            self.data["joinStyle"] = join_style
            self.data["style"] = style
            self.data["pattern"] = self.my_pen.dashPattern()
            self.data["patternOffset"] = self.my_pen.dashOffset()

    def get_drawing_events(self, scene_info):
        self.path = QPainterPath()
        self.pathItem = QGraphicsPathItem()
        point = QPointF(scene_info["position"][0], scene_info["position"][1])
        if scene_info["event"] == "mousePressEvent" and scene_info["state"] is False:
            self.path = QPainterPath()
            color = QColor(scene_info["color"])
            size = scene_info["width"]
            pattern = scene_info["pattern"]

            style = getattr(Qt.PenStyle, scene_info["style"])

            self.my_pen = QPen(color, size)
            self.my_pen.setStyle(style)
            self.my_pen.setDashPattern(scene_info["pattern"])
            self.path.moveTo(point)
            self.pathItem.setPen(self.my_pen)
            self.pathItem.setPath(self.path)

            self.addItem(self.pathItem)

        elif scene_info["state"] is True and scene_info["event"] == "mouseMoveEvent":
            self.path.lineTo(point)
            color = QColor(scene_info["color"])
            size = scene_info["width"]
            pattern = scene_info["pattern"]

            style = getattr(Qt.PenStyle, scene_info["style"])

            self.my_pen = QPen(color, size)
            self.my_pen.setStyle(style)
            self.my_pen.setDashPattern(scene_info["pattern"])
            self.pathItem.setPen(self.my_pen)
            self.pathItem.setPath(self.path)

            self.addItem(self.pathItem)

        elif scene_info["event"] == "mouseReleaseEvent" and scene_info["state"] is False:
            pass

    # def scene_file(self):
    #     data = {
    #         'lines': [],  # stores info of each line drawn
    #         'scene_rect': [self.width(), self.height()],  # stores dimension of scene
    #         'color': self.color.name(),  # store the color used
    #         'size': self.size  # store the size of the pen
    #     }
    #     for item in self.items():
    #         if isinstance(item, QGraphicsPathItem):
    #             line_data = {
    #                 'color': item.pen().color().name(),
    #                 'width': item.pen().widthF(),
    #                 # 'color': self.my_pen.color().name(),
    #                 # 'width': self.my_pen.widthF(),
    #                 'points': []  # stores the (X,Y) coordinate of the line
    #             }
    #
    #             # Extract points from the path
    #             for subpath in item.path().toSubpathPolygons():  # to SubpathPolygons method is used to break down
    #                 # the complex line into sub parts and store it
    #                 line_data['points'].extend([(point.x(), point.y()) for point in subpath])
    #
    #             data['lines'].append(line_data)
    #     # print(data)
    #     signal_manager.data_sig.emit(data)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.undo_flag = False
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

    def Close_window(self):
        self.close()

    def New_file(self):
        new_file = MainWindow()
        new_file.show()

    def change_size(self):
        self.scene.change_size(self.dial.value())

    def undo(self):
        if self.scene.items():
            latest_item = self.scene.items()
            print(self.scene.items())
            self.redo_list.append(latest_item)
            self.scene.removeItem(latest_item[0])
            signal_manager.function_call.emit(True)
        # if self.pb_Undo.clicked:
        #     # print('Clicked')
        #     self.undo_flag = True
        #     signal_manager.data_updated.emit(self.undo_flag)
        #     self.scene_file(self.undo_flag)
        #     print('removed')
        # else:
        #     print('Not Clicked')
        #     signal_manager.data_updated.emit(False)

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
        print(f"Eraser paths : {self.scene.drawn_paths} ")
        # self.erase_path(self.scene.drawn_paths)

    def button_clicked(self):
        sender_button = self.sender()
        for btn in self.list_of_buttons:
            if btn is not sender_button:
                btn.setChecked(False)

    def erase_path(self, path):
        for item in self.scene.items():
            if isinstance(item, QGraphicsPathItem):
                if item.path() == path:
                    self.scene.removeItem(item)
                    break

    def scene_file(self, flag):
        self.undo_flag = flag
        data = {
            'lines': [],  # stores info of each line drawn
            'scene_rect': [self.scene.width(), self.scene.height()],  # stores dimension of scene
            'color': self.scene.color.name(),  # store the color used
            'size': self.scene.size  # store the size of the pen
        }
        # self.scene.items().reverse()
        for item in reversed(self.scene.items()):
            if isinstance(item, QGraphicsPathItem):
                line_data = {
                    'color': item.pen().color().name(),
                    'width': item.pen().widthF(),
                    # 'color': self.my_pen.color().name(),
                    # 'width': self.my_pen.widthF(),
                    'points': []  # stores the (X,Y) coordinate of the line
                }

                # Extract points from the path
                for subpath in item.path().toSubpathPolygons():  # to SubpathPolygons method is used to break down
                    # the complex line into sub parts and store it
                    line_data['points'].extend([(point.x(), point.y()) for point in subpath])

                data['lines'].append(line_data)
        # print(data)
        signal_manager.data_sig.emit(data, self.undo_flag)

    def track_mouse_event(self, e):
        if e is True:
            self.scene_file(False)
        else:
            pass


def init_gui():
    # start_server(server)

    # For client side
    # binding the signals to specific functions of server
    # signal_manager.send_info.connect(server.broadcast)
    # signal_manager.action_signal.connect(server.channel_broadcast)

    # Client side connections
    app = QApplication()
    window = MainWindow()

    client = MyClient()
    start_client(client)
    # signal_manager.send_info.connect(client.ping_server)
    signal_manager.data_sig.connect(client.ping_server)
    signal_manager.function_call.connect(window.track_mouse_event)
    signal_manager.data_updated.connect(window.scene_file)

    window.show()

    app.exec()


if __name__ == '__main__':
    #     app = QApplication()
    #
    #     window = MainWindow()
    #     window.show()
    #
    #     app.exec()
    init_gui()
