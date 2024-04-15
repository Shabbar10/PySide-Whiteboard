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
    Signal
)

from Whiteboard.WhiteboardApplication.UI.board import Ui_MainWindow
from network import signal_manager, MyServer, start_server
import json

############################################################################################################
server = MyServer()


def qcolor_to_dict(color):
    return {'red': color.red(), 'green': color.green(), 'blue': color.blue(), 'alpha': color.alpha()}


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
        self.action_state = 0
        self.render_info = {"position": (0, 0),
                            "color": None,
                            "pensize": 1,
                            "widthF": None,
                            "width": None,
                            "capStyle": "",
                            "joinStyle": "",
                            "style": "",
                            "pattern": None,
                            "patternOffset": None
                            }
        self.timer = QTimer()
        self.timer.timeout.connect(self.send_updates)
        self.timer.start(3)  # Adjust the interval as needed
        self.pos = []
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

            self.pos.append(self.previous_position.y())
            self.pos.append(self.previous_position.x())
            self.pos.clear()
            ############################################################################################################

            self.data = [self.previous_position, self.my_pen.color(), self.my_pen.widthF(), self.my_pen.width(),
                         self.my_pen.capStyle(), self.my_pen.joinStyle(), self.my_pen.style(),
                         self.my_pen.dashPattern(), self.my_pen.dashOffset()]

            self.send_updates()
            # self._configure_updates()
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
            # self.pos = [self.previous_position.x(), self.previous_position.y()]
            self.pos.append(self.previous_position.y())
            self.pos.append(self.previous_position.x())
            self.send_updates()
            # self._configure_updates()
            ############################################################################################################

            # signal_manager.send_info.emit(self.render_info)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            self.data.clear()
            self.pos.append(self.previous_position.y())
            self.pos.append(self.previous_position.x())

            self.previous_position = None
            self.pos.clear()
            # self._configure_updates()
            # signal_manager.send_info.emit(0,self.render_info)
            self.send_updates()

############################################################################################################

    def _configure_updates(self):
        # if len(self.pos) >= 2:

        if len(self.pos) >= 2:
            color = self.my_pen.color().name()
            position = (self.pos[0], self.pos[1])
            width_f = self.my_pen.widthF()
            w = self.my_pen.width()
            cp_style = self.pen_cap_style_to_string(self.my_pen.capStyle())
            join_style = self.pen_join_style_to_string(self.my_pen.joinStyle())
            style = self.pen_style_to_string(self.my_pen.style())
            pattern = self.my_pen.dashPattern()
            pat_offset = self.my_pen.dashOffset()

            self.render_info["position"] = position
            self.render_info["color"] = color
            self.render_info["widthF"] = width_f
            self.render_info["width"] = w

            self.render_info["capStyle"] = cp_style
            self.render_info["joinStyle"] = join_style
            self.render_info["style"] = style

            self.render_info["pattern"] = pattern
            self.render_info["patternOffset"] = pat_offset
            self.render_info["pensize"] = self.size

            self.pos.clear()




    ############################################################################################################



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
    def pen_style_to_string(self,pen_style):
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
############################################################################################################
    def send_updates(self):
        self._configure_updates()
        # print(self.action_state)
        # print(self.render_info)

        signal_manager.action_signal.emit(self.action_state, self.render_info)
        # data_to_send.clear()

############################################################################################################

    def get_drawn_paths(self):
        return self.drawn_paths

    def clear_drawn_paths(self):
        self.drawn_paths = []
        self.clear()


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
    # binding the signals to specific functions of server

    app = QApplication()
    window = MainWindow()
    start_server(server)
    # signal_manager.send_info.connect(server.channel_broadcast)


    # Connect the signals


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
    signal_manager.action_signal.connect(server.channel_broadcast)

    init_gui()
