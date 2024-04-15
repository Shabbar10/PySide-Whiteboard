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
    QTimer,
    QPointF
)

from Whiteboard.WhiteboardApplication.UI.board import Ui_MainWindow
from client_net import signal_manager, MyClient, start_client
import json

############################################################################################################
client = MyClient()
############################################################################################################


class BoardScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 600, 500)

        # self.render_info.setdefault("Not defined yet")
        self.my_pen = None
        self.drawn_paths = []

        self.path = None
        self.previous_position = None
        self.drawing = False
        self.color = QColor("#000000")
        self.size = 1
        self.pathItem = None
        ############################################################################################################
        self.data = []
        self.render_info = {"position": None,
                            "color": None,
                            "widthF": None,
                            "width": None,
                            "capStyle": None,
                            "joinStyle": None,
                            "style": None,
                            "pattern": None,
                            "patternOffset": None
                            }
        self.timer = QTimer()
        self.timer.timeout.connect(self.send_updates)
        self.timer.start(3)  # Adjust the interval as needed
        ############################################################################################################

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
            # self.data.append(self.previous_position)

            ############################################################################################################

            self.data = [self.previous_position, self.my_pen.color(), self.my_pen.widthF(), self.my_pen.width(),
                         self.my_pen.capStyle(), self.my_pen.joinStyle(), self.my_pen.style(),
                         self.my_pen.dashPattern(), self.my_pen.dashOffset()]

            self._configure_updates()
            ############################################################################################################

            # signal_manager.send_info.emit(self.render_info)

    def mouseMoveEvent(self, event):
        if self.drawing:
            curr_position = event.scenePos()
            self.path.lineTo(curr_position)
            self.pathItem.setPath(self.path)
            self.previous_position = curr_position
            ############################################################################################################

            self.data.clear()
            self.data = [self.previous_position, self.my_pen.color(), self.my_pen.widthF(), self.my_pen.width(),
                         self.my_pen.capStyle(), self.my_pen.joinStyle(), self.my_pen.style(),
                         self.my_pen.dashPattern(), self.my_pen.dashOffset()]

            self._configure_updates()
            ############################################################################################################

            # signal_manager.send_info.emit(self.render_info)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.previous_position = None
            self.drawing = False
            self.data.clear()
            self._configure_updates()
            # signal_manager.send_info.emit(self.render_info)

############################################################################################################

    def _configure_updates(self):
        self.render_info["position"] = self.previous_position
        self.render_info["color"] = self.my_pen.color()
        self.render_info["widthF"] = self.my_pen.widthF()
        self.render_info["width"] = self.my_pen.width()
        self.render_info["capStyle"] = self.my_pen.capStyle()
        self.render_info["joinStyle"] = self.my_pen.joinStyle()
        self.render_info["style"] = self.my_pen.style()
        self.render_info["pattern"] = self.my_pen.dashPattern()
        self.render_info["patternOffset"] = self.my_pen.dashOffset()

############################################################################################################

############################################################################################################
    def send_updates(self):
        if self.drawing:
            data_to_send = self.render_info
            self._configure_updates()
            signal_manager.send_info.emit(data_to_send)
            data_to_send.clear()
        else:
            pass
############################################################################################################

    def get_drawn_paths(self):
        return self.drawn_paths

    def clear_drawn_paths(self):
        self.drawn_paths = []
        self.clear()

    ############################################################################################################
    def retrace_scene(self, scene_info: dict):
        point = QPointF(scene_info["position"])

        if type(scene_info) is not dict:
            print("DATA TRANSMISSION ERROR(TypeError)")
        else:
            if self.drawing is False:
                self.path = QPainterPath()
                self.pathItem = QGraphicsPathItem()
                self.path.moveTo(point)

                self.my_pen = QPen(scene_info["color"], scene_info["pensize"])
                self.my_pen.setCapStyle(scene_info["capStyle"])
                self.my_pen.setWidth(scene_info["width"])
                self.my_pen.setWidthF(scene_info["widthF"])
                self.my_pen.setStyle(scene_info["style"])
                self.my_pen.setDashPattern(scene_info["pattern"])
                self.my_pen.setDashOffset(scene_info["patternOffset"])

                self.pathItem.setPen(self.my_pen)
                self.addItem(self.pathItem)
                self.drawing = True

            else:
                # curr_position = scene_info["position"]
                self.my_pen = QPen(scene_info["color"], scene_info["pensize"])
                self.my_pen.setCapStyle(scene_info["capStyle"])
                self.my_pen.setWidth(scene_info["width"])
                self.my_pen.setWidthF(scene_info["widthF"])
                self.my_pen.setStyle(scene_info["style"])
                self.my_pen.setDashPattern(scene_info["pattern"])
                self.my_pen.setDashOffset(scene_info["patternOffset"])

                self.path.lineTo(point)
                self.pathItem.setPath(self.path)



############################################################################################################

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
                for item in self.scene.items():
                    if isinstance(item, QGraphicsPathItem):
                        line_data = {
                            'color': item.pen().color().name(),
                            'width': item.pen().widthF(),
                            'points': []  # stores the (X,Y) coordinate of the line
                        }

                        # Extract points from the path
                        for subpath in item.path().toSubpathPolygons():
                            # to SubpathPolygons method is used to break down
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




############################################################################################################


def init_gui():
    # start_server(server)

    # For client side
    # binding the signals to specific functions of server
    # signal_manager.send_info.connect(server.broadcast)
    # signal_manager.action_signal.connect(server.channel_broadcast)

    # Client side connections
    app = QApplication()
    window = MainWindow()

    signal_manager.retrace_canvas.connect(window.scene.retrace_scene)

    window.show()

    app.exec()


############################################################################################################


if __name__ == '__main__':
    # app = QApplication()
    #
    # window = MainWindow()
    # window.show()
    #
    # app.exec()
    start_client(client)
    init_gui()
