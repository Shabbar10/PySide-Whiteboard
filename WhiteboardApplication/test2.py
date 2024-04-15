from PySide6.QtWidgets import (
    QMainWindow,
    QGraphicsScene,
    QApplication,
    QGraphicsPathItem,
    QColorDialog,
    QFileDialog,
    QGraphicsEllipseItem,
    QGraphicsRectItem,
    QPushButton,
    QButtonGroup
)

from PySide6.QtGui import (
    QPen,
    Qt,
    QPainter,
    QPainterPath,
    QColor
)

from PySide6.QtCore import (
    Qt,
    QRectF
)
import json
from Whiteboard.WhiteboardApplication.UI.board import Ui_MainWindow

class BoardScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 600, 500)

        self.path = None
        self.previous_position = None
        self.drawing = False
        self.color = QColor("#000000")
        self.size = 1
        self.pathItem = None
        self.drawn_paths = []
        self.current_tool = None
        self.line_mode = False
        self.ellipse_mode = False
        self.rectangle_mode = False

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

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            if self.line_mode or self.ellipse_mode or self.rectangle_mode:
                self.pathItem = None
            else:
                self.drawn_paths.append(self.path)
                self.pathItem = None

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
        self.list_of_buttons = [self.pb_Pen, self.pb_Eraser, self.pb_line, self.pb_ellipse, self.pb_rectangle]

        self.pb_Pen.setChecked(True)
        self.pb_Pen.clicked.connect(self.button_clicked)
        self.pb_Eraser.clicked.connect(self.button_clicked)
        self.pb_line.clicked.connect(self.button_clicked)
        self.pb_ellipse.clicked.connect(self.button_clicked)
        self.pb_rectangle.clicked.connect(self.button_clicked)

        self.current_color = QColor("#000000")

        ############################################################################################################

        self.actionClear.triggered.connect(self.clear_canvas)
        self.actionCoolDude.triggered.connect(self.New_file)
        self.actionClose_2.triggered.connect(self.Close_window)
        self.actionSave_As.triggered.connect(self.save_file)
        self.actionNew_3.triggered.connect(self.load_file)
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
        self.pb_line.clicked.connect(self.toggle_line_mode)
        self.pb_ellipse.clicked.connect(self.toggle_ellipse_mode)
        self.pb_rectangle.clicked.connect(self.toggle_rectangle_mode)
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
                'lines': [],
                'scene_rect': [self.scene.width(), self.scene.height()],
                'color': self.scene.color.name(),
                'size': self.scene.size
            }
            for item in reversed(self.scene.items()):
                if isinstance(item, QGraphicsPathItem):
                    line_data = {
                        'color': item.pen().color().name(),
                        'width': item.pen().widthF(),
                        'points': []
                    }
                    for subpath in item.path().toSubpathPolygons():
                        line_data['points'].extend([(point.x(), point.y()) for point in subpath])
                    data['lines'].append(line_data)

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

    def save(self):
        if self.current_file:
            data = {
                'lines': [],
                'scene_rect': [self.scene.width(), self.scene.height()],
                'color': self.scene.color.name(),
                'size': self.scene.size
            }
            for item in reversed(self.scene.items()):
                if isinstance(item, QGraphicsPathItem):
                    line_data = {
                        'color': item.pen().color().name(),
                        'width': item.pen().widthF(),
                        'points': []
                    }
                    for subpath in item.path().toSubpathPolygons():
                        line_data['points'].extend([(point.x(), point.y()) for point in subpath])
                    data['lines'].append(line_data)

            with open(self.current_file, 'w') as file:
                json.dump(data, file)
        else:
            self.save_file()

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

    def deselect_current_mode(self):
        self.scene.line_mode = False
        self.scene.ellipse_mode = False
        self.scene.rectangle_mode = False
        self.pb_line.setChecked(False)
        self.pb_ellipse.setChecked(False)
        self.pb_rectangle.setChecked(False)

    def button_clicked(self):
        self.deselect_current_mode()

        sender_button = self.sender()
        for btn in self.list_of_buttons:
            if btn is not sender_button:
                btn.setChecked(False)

    def toggle_line_mode(self):
        self.deselect_current_mode()
        self.scene.set_line_mode(True)
        self.pb_line.setChecked(True)
        self.scene.set_tool("Line")

    def toggle_ellipse_mode(self):
        self.deselect_current_mode()
        self.scene.set_ellipse_mode(True)
        self.pb_ellipse.setChecked(True)
        self.scene.set_tool("Ellipse")

    def toggle_rectangle_mode(self):
        self.deselect_current_mode()
        self.scene.set_rectangle_mode(True)
        self.pb_rectangle.setChecked(True)
        self.scene.set_tool("Rectangle")

if __name__ == '__main__':
    app = QApplication()

    window = MainWindow()
    window.show()

    app.exec()
