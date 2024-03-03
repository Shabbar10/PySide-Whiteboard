from PySide6.QtWidgets import (
    QMainWindow,
    QGraphicsScene,
    QApplication,
    QGraphicsPathItem,
    QColorDialog,
)

from PySide6.QtGui import (
    QPen,
    Qt,
    QPainter,
    QPainterPath,
    QColor,
)

from PySide6.QtCore import (
    Qt
)

from WhiteboardApplication.UI.board import Ui_MainWindow


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
            my_pen = QPen(self.color, self.size)
            my_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            self.pathItem.setPen(my_pen)
            self.addItem(self.pathItem)

    def mouseMoveEvent(self, event):
        if self.drawing:
            curr_position = event.scenePos()
            self.path.lineTo(curr_position)
            self.pathItem.setPath(self.path)
            self.previous_position = curr_position

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.previous_position = None
            self.drawing = False


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


if __name__ == '__main__':
    app = QApplication()

    window = MainWindow()
    window.show()

    app.exec()
