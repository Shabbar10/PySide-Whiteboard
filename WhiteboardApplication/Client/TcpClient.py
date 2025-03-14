import sys
import cProfile, pstats


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
    QGraphicsRectItem,
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
    QObject,
    Signal,
    Slot,
    QTimer,
    QRectF,
    QThread,
)
import json
from TcpClientNet import start_client, MyClient, signal_manager
from WhiteboardApplication.UI.board import Ui_MainWindow
from collections import deque

itemTypes = set()
circular_recv_buffer = deque(maxlen=20)
circular_send_buffer = deque(maxlen=20)
buffer_flag = 0
login_flag = False
itemTypes = set()
validation_dict = {'Atharva': 'ghanekar', 'Abubakar': 'siddiq', 'Shabbar': 'adamjee', 'Hussain': 'ceyloni', '': ''}


class BoardScene(QGraphicsScene):
    def __init__(self):
        super().__init__()

        self.undo_flag = False
        self.data_list = []
        self.path : QPainterPath = None
        self.previous_position = None
        self.drawing = False
        self.color = QColor("#000000")
        self.size = 5
        self.pathItem = None
        self.drawn_paths = []
        self.my_pen = None
        self.start_pos = None

        # Since we're breaking lines into multiple items if they get to long,
        # we need a better way to deal with undo and redo.
        # So we group line segments of the same line into 1 'stroke group'
        self.stroke_groups = []
        self.current_stroke_group = []

        self.current_tool = None
        self.pen_mode = True
        self.line_mode = False
        self.ellipse_mode = False
        self.rectangle_mode = False
        self.eraser_mode = False;

        self.last_sent_point_index = 0
        # self.send_timer = QTimer()
        # self.send_timer.setInterval(50)
        # self.send_timer.timeout.connect(self.send_path_segment)

        self.serializer_worker : SceneSerializerWorker = None
        self.serializer_thread : QThread = None
        self.builder_worker : SceneBuilderWorker = None
        self.builder_thread : QThread = None
        self.setup_threads()


    def setup_threads(self):
        self.serializer_worker = SceneSerializerWorker(self)
        self.serializer_thread = QThread()
        self.serializer_worker.moveToThread(self.serializer_thread)
        self.serializer_thread.start()

        self.builder_worker = SceneBuilderWorker(self)
        self.builder_thread = QThread()
        self.builder_worker.moveToThread(self.builder_thread)
        self.builder_thread.start()

    def cleanup_threads(self):
        workers = [self.serializer_worker, self.builder_worker]
        threads = [self.serializer_thread, self.builder_thread]

        for worker, thread in zip(workers, threads):
            worker.deleteLater()
            thread.quit()
            thread.wait(3000)
            if thread.isRunning():
                thread.terminate()
            thread.deleteLater()

        print("All threads and workers cleaned up.")

    def change_color(self, color):
        self.color = color

    def change_size(self, size):
        self.size = size

    def set_tool(self, tool):
        self.current_tool = tool

    def set_pen_mode(self, mode):
        self.pen_mode = mode
        self.rectangle_mode = False
        self.line_mode = False
        self.ellipse_mode = False
        self.eraser_mode = False

    def set_rectangle_mode(self, mode):
        self.rectangle_mode = mode
        self.pen_mode = False
        self.line_mode = False
        self.ellipse_mode = False
        self.eraser_mode = False

    def set_line_mode(self, mode):
        self.line_mode = mode
        self.pen_mode = False
        self.ellipse_mode = False
        self.rectangle_mode = False
        self.eraser_mode = False

    def set_ellipse_mode(self, mode):
        self.ellipse_mode = mode
        self.pen_mode = False
        self.line_mode = False
        self.rectangle_mode = False
        self.eraser_mode = False

    def set_eraser_mode(self, mode):
        self.eraser_mode = mode
        self.pen_mode = False
        self.ellipse_mode = False
        self.line_mode = False
        self.rectangle_mode = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print("Mouse clicked")
            self.drawing = True
            self.current_stroke_group = []

            if self.rectangle_mode:
                self.start_pos = event.scenePos()
                self.pathItem = QGraphicsRectItem()
                self.pathItem.setPen(QPen(self.color, self.size))
                self.addItem(self.pathItem)
                self.current_stroke_group.append(self.pathItem)
            elif self.line_mode:
                self.start_pos = event.scenePos()
                self.pathItem = QGraphicsPathItem()
                self.pathItem.setPen(QPen(self.color, self.size))
                self.addItem(self.pathItem)
                self.current_stroke_group.append(self.pathItem)
            elif self.ellipse_mode:
                self.start_pos = event.scenePos()
                self.pathItem = QGraphicsEllipseItem()
                self.pathItem.setPen(QPen(self.color, self.size))
                self.addItem(self.pathItem)
                self.current_stroke_group.append(self.pathItem)
            else:
                self.start_pos = event.scenePos()
                self.previous_position = event.scenePos()

                if self.pathItem is None:
                    self.path = QPainterPath()
                    self.path.moveTo(self.previous_position)
                    self.pathItem = QGraphicsPathItem()
                    my_pen = QPen(self.color, self.size)
                    my_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                    self.pathItem.setPen(my_pen)
                    self.addItem(self.pathItem)
                    self.current_stroke_group.append(self.pathItem)
                    self.last_sent_point_index = 0
                    # self.send_timer.start()

    def mouseMoveEvent(self, event):
        if self.drawing:
            curr_position = event.scenePos()

            if self.rectangle_mode:
                rect = QRectF(self.start_pos, event.scenePos()).normalized()
                self.pathItem.setRect(rect)
            elif self.line_mode:
                path = QPainterPath()
                path.moveTo(self.start_pos)
                path.lineTo(event.scenePos())
                self.pathItem.setPath(path)
            elif self.ellipse_mode:
                print(f"Start pos = {self.start_pos}")
                print(f"Event pos = {event.scenePos()}")
                rect = QRectF(self.start_pos, event.scenePos()).normalized()
                self.pathItem.setRect(rect)
            elif self.eraser_mode:
                eraser_size = self.size * 5
                eraser_rect = QRectF(
                    curr_position.x() - eraser_size / 2,
                    curr_position.y() - eraser_size / 2,
                    eraser_size, eraser_size
                )

                items_to_erase = self.items(eraser_rect)
                for item in items_to_erase:
                    if item != self.pathItem:
                        self.removeItem(item)

            else: # If freehand drawing
                if self.path.elementCount() > 1:
                    control_point = self.previous_position
                    endpoint = (curr_position + self.previous_position) / 2
                    self.path.quadTo(control_point, endpoint)
                else:
                    self.path.lineTo(curr_position)

                self.pathItem.setPath(self.path)
                self.previous_position = curr_position

                if self.path.elementCount() > 30:
                    # Get the last point of the current path
                    last_element = self.path.elementAt(self.path.elementCount() - 1)
                    last_point = (last_element.x, last_element.y)

                    self.finalize_current_path()

                    self.path = QPainterPath()
                    self.path.moveTo(last_point[0], last_point[1])

                    self.pathItem = QGraphicsPathItem()

                    my_pen = QPen(self.color, self.size)
                    my_pen.setCapStyle(Qt.PenCapStyle.RoundCap)

                    self.pathItem.setPen(my_pen)
                    self.addItem(self.pathItem)

                    self.current_stroke_group.append(self.pathItem)

                    self.path.lineTo(curr_position.x(), curr_position.y())
                    self.pathItem.setPath(self.path)

                    self.last_sent_point_index = 0

        # Expand scene if drawing near the edge
        buffer = 50
        current_rect = self.sceneRect()

        if event.scenePos().x() > current_rect.right() - buffer:
            self.setSceneRect(current_rect.adjusted(0, 0, 500, 0))
            print("expand right")
        if event.scenePos().y() > current_rect.bottom() - buffer:
            self.setSceneRect(current_rect.adjusted(0, 0, 0, 500))
            print("expand down")
        if event.scenePos().x() < current_rect.left() + buffer:
            self.setSceneRect(current_rect.adjusted(-500, 0, 0, 0))
            print("expand left")
        if event.scenePos().y() < current_rect.top() + buffer:
            self.setSceneRect(current_rect.adjusted(0, -500, 0, 0))
            print("expand up")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

            if self.pen_mode:
                print("Mouse release, pen mode")
                curr_pos = event.scenePos()
                delta_x = abs(curr_pos.x() - self.start_pos.x())
                delta_y = abs(curr_pos.y() - self.start_pos.y())
                if delta_x <= 10 and delta_y <= 10:
                    print("Drawing dot")
                    dot_item = QGraphicsEllipseItem()
                    dot_item.setPen(QPen(QColor(self.color), self.size))
                    dot_item.setBrush(QColor(self.color))

                    size = self.size
                    x = self.start_pos.x() - self.size / 2
                    y = self.start_pos.y() - self.size / 2
                    dot_rect = QRectF(x, y, size, size)
                    dot_item.setRect(dot_rect)
                    self.addItem(dot_item)


            if self.line_mode or self.ellipse_mode or self.rectangle_mode:
                signal_manager.data_updated.emit(False)
            else:
                self.send_path_segment(final=True)

            if self.current_stroke_group:
                self.stroke_groups.append(self.current_stroke_group)
                self.current_stroke_group = []

            self.pathItem = None
        super().mouseReleaseEvent(event)

    def finalize_current_path(self):
        if self.pathItem and self.path.elementCount() > 1:
            self.send_path_segment(final=True)

    def send_path_segment(self, final=False):
        # If pathItem is none or there have been no new points added
        if not self.pathItem or self.path.elementCount() <= self.last_sent_point_index:
            return

        current_count = self.path.elementCount()
        if current_count - self.last_sent_point_index > 5 or final:
            signal_manager.data_updated.emit(False)
            self.last_sent_point_index = current_count

    def scene_file(self, flag):
        if self.items():
            new_item = self.items()[0]
            #print(f"Newest item: {new_item}")
            self.serializer_worker.serialize_signal.emit(new_item, flag)

    def build_scene_file(self, data):
        self.builder_worker.build_scene.emit(data)

class SceneBuilderWorker(QObject):
    build_scene = Signal(dict)

    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self.build_scene.connect(self.add_to_scene)

    @Slot(dict)
    def add_to_scene(self, data):
        scene = self.scene
        scene_file = data['scene_info']

        try:
            scene.change_color(QColor(scene_file['color']))
            scene.change_size(scene_file['width'])

            if scene_file['type'] == 'path':
                is_complete = scene_file.get('is_complete', True)

                path = QPainterPath()

                if len(scene_file['points']) > 0:
                    path.moveTo(scene_file['points'][0][0], scene_file['points'][0][1])
                    for line_data in scene_file['points'][1:]:
                        path.lineTo(line_data[0], line_data[1])

                    pathItem = QGraphicsPathItem(path)
                    my_pen = QPen(QColor(scene_file['color']), scene_file['width'])
                    my_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                    pathItem.setPen(my_pen)
                    #print(f"Adding path: {pathItem}")
                    scene.addItem(pathItem)

            elif scene_file['type'] == 'rectangle':
                rect_data = scene_file['points']
                rect = QRectF(rect_data[0], rect_data[1], rect_data[2], rect_data[3])
                rectItem = QGraphicsRectItem(rect)
                my_pen = QPen(QColor(scene_file['color']), scene_file['width'])
                rectItem.setPen(my_pen)
                #print(f"Adding rectangle: {rectItem}")
                scene.addItem(rectItem)

            elif scene_file['type'] == 'ellipse':
                ellipse_data = scene_file['points']
                ellipse = QRectF(ellipse_data[0], ellipse_data[1], ellipse_data[2], ellipse_data[3])
                ellipseItem = QGraphicsEllipseItem(ellipse)
                my_pen = QPen(QColor(scene_file['color']), scene_file['width'])
                ellipseItem.setPen(my_pen)
                # print(f"Adding ellipse: {ellipseItem}")
                scene.addItem(ellipseItem)

            scene.update()
            for view in scene.views():
                view.viewport().update()
                view.update()
                #view.repaint()

            QTimer.singleShot(0, QApplication.instance().processEvents)
            # QApplication.processEvents()

        except IndexError as e:
            print(e)
        except Exception as e:
            print(e)


class SceneSerializerWorker(QObject):
    serialize_signal = Signal(QObject, bool)

    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self.serialize_signal.connect(self.serialize_item)

    @Slot(object, bool)
    def serialize_item(self, item, flag):
        data = {}

        if isinstance(item, QGraphicsPathItem):
            path = item.path()
            points = []

            for i in range(path.elementCount()):
                element = path.elementAt(i)
                points.append((element.x, element.y))

            line_data = {
                'type': 'path',
                'color': item.pen().color().name(),
                'width': item.pen().width(),
                #'points': [(point.x(), point.y()) for subpath in item.path().toSubpathPolygons() for point in subpath]
                'points': points,
                'is_complete': not item.scene().drawing
            }

            print(f"Length of points: {len(points)}")
            if not item.scene().drawing or len(points) > 100:
                reduced_points = self.reduce_points(line_data['points'])
                line_data['points'] = reduced_points
            else:
                line_data['points'] = points

            data = line_data

        elif isinstance(item, QGraphicsRectItem):
            rect_data = {
                'type': 'rectangle',
                'color': item.pen().color().name(),
                'width': item.pen().width(),
                'points': [item.rect().x(), item.rect().y(), item.rect().width(), item.rect().height()]
            }
            data = rect_data
        elif isinstance(item, QGraphicsEllipseItem):
            ellipse_data = {
                'type': 'ellipse',
                'color': item.pen().color().name(),
                'width': item.pen().width(),
                'points': [item.rect().x(), item.rect().y(), item.rect().width(), item.rect().height()]
            }
            data = ellipse_data
        #print(f"Serialized data: {data}")
        signal_manager.data_serialized.emit(data, flag)

    def reduce_points(self, points, tolerance=1.0):
        print(f"Reduce function called")
        # print(f"Reduce function points received: {points}")
        print(f"Reduce function points received length: {len(points)}")
        if len(points) < 3:
            return points

        reduced = [points[0]] # Keep 1st point as is

        for i in range(1, len(points) - 1):
            prev_x, prev_y = reduced[-1]
            curr_x, curr_y = points[i]
            next_x, next_y = points[i + 1]

            v1 = (curr_x - prev_x, curr_y - prev_y)
            v2 = (next_x - curr_x, next_y - curr_y)

            if abs(v1[0] - v2[0]) > tolerance or abs(v1[1] - v2[1]) > tolerance:
                reduced.append((curr_x, curr_y))

        reduced.append(points[-1])
        #print(f"Reduce function final points: {reduced}")
        print(f"Reduce function final points length: {len(reduced)}")
        return reduced


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, client):
        super().__init__()
        self.setupUi(self)
        self.client = client
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
        #self.pb_Eraser.clicked.connect(lambda e: self.color_changed(QColor("#FFFFFF")))

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
        self.resize_scene()

        self.redo_list = []
        self.current_file = None

    def wheelEvent(self, event):
        scroll_delta = event.angleDelta().y()  # Detect scroll direction
        current_rect = self.scene.sceneRect()

        if scroll_delta > 0:  # Scrolling up
            self.scene.setSceneRect(current_rect.adjusted(-500, -500, 500, 500))  # Expand in all directions
        elif scroll_delta < 0:  # Scrolling down
            self.scene.setSceneRect(current_rect.adjusted(-500, -500, 500, 500))  # Expand in all directions

        super().wheelEvent(event)

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