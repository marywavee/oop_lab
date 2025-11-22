import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QToolBar, QColorDialog
)
from PyQt6.QtGui import (
    QAction, QActionGroup, QPainter, QPen, QBrush,
    QColor, QKeySequence
)
from PyQt6.QtCore import Qt, QPoint, QRect


class ShapeStorage:
    def __init__(self):
        self._items = []

    def add(self, shape):
        self._items.append(shape)

    def remove(self, shape):
        if shape in self._items:
            self._items.remove(shape)

    def clear(self):
        self._items.clear()

    def __iter__(self):
        return iter(self._items)

    def __reversed__(self):
        return reversed(self._items)

    def __len__(self):
        return len(self._items)


class Shape:
    def __init__(self, color):
        self.color = color
        self.selected = False

    def draw(self, painter): raise NotImplementedError
    def bounding_rect(self) -> QRect: raise NotImplementedError
    def contains(self, point: QPoint) -> bool: raise NotImplementedError
    def move_by(self, dx: int, dy: int, canvas: QWidget) -> bool: raise NotImplementedError


class Circle(Shape):
    def __init__(self, center: QPoint, radius: int = 40, color=QColor):
        super().__init__(color)
        self.center = QPoint(center)
        self.radius = radius

    def draw(self, painter: QPainter):
        painter.setPen(QPen(self.color, 3))
        painter.setBrush(QBrush(self.color) if self.selected else QBrush())
        painter.drawEllipse(self.center, self.radius, self.radius)

        if self.selected:
            painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.DashLine))
            painter.setBrush(QBrush())
            painter.drawEllipse(self.center, self.radius + 6, self.radius + 6)

    def bounding_rect(self) -> QRect:
        r = self.radius + 10
        return QRect(self.center.x() - r, self.center.y() - r, r * 2, r * 2)

    def contains(self, point: QPoint) -> bool:
        return (point - self.center).manhattanLength() <= self.radius + 10

    def move_by(self, dx: int, dy: int, canvas: QWidget) -> bool:
        new_center = self.center + QPoint(dx, dy)
        test_rect = self.bounding_rect().translated(dx, dy)
        if canvas.rect().contains(test_rect):
            self.center = new_center
            return True
        return False


class Rectangle(Shape):
    def __init__(self, x: int, y: int, w: int = 100, h: int = 70, color=QColor):
        super().__init__(color)
        self.rect = QRect(x, y, w, h)

    def draw(self, painter: QPainter):
        painter.setPen(QPen(self.color, 3))
        painter.setBrush(QBrush(self.color) if self.selected else QBrush())
        painter.drawRect(self.rect)

        if self.selected:
            painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.DashLine))
            painter.setBrush(QBrush())
            painter.drawRect(self.rect.adjusted(-6, -6, 12, 12))

    def bounding_rect(self) -> QRect:
        return self.rect.adjusted(-10, -10, 20, 20)

    def contains(self, point: QPoint) -> bool:
        return self.rect.adjusted(-10, -10, 10, 10).contains(point)

    def move_by(self, dx: int, dy: int, canvas: QWidget) -> bool:
        new_rect = self.rect.translated(dx, dy)
        test_rect = self.bounding_rect().translated(dx, dy)
        if canvas.rect().contains(test_rect):
            self.rect = new_rect
            return True
        return False


class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.storage = ShapeStorage()
        self.current_color = QColor("#0066ff")
        self.current_shape_type = "circle"        # по умолчанию — круги
        self.drag_start = None
        self.selected_shapes = set()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#fafafa"))

        for shape in self.storage:
            shape.draw(painter)

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = event.pos()

        hit = None
        for shape in reversed(list(self.storage)):
            if shape.contains(pos):
                hit = shape
                break

        ctrl = event.modifiers() & Qt.KeyboardModifier.ControlModifier

        if hit:
            if ctrl:
                self.toggle_selection(hit)
            else:
                self.deselect_all()
                self.select_shape(hit)
        else:
            if not ctrl:
                self.deselect_all()
            shape = None
            if self.current_shape_type == "circle":
                shape = Circle(pos, 40, self.current_color)
            elif self.current_shape_type == "rectangle":
                shape = Rectangle(pos.x() - 50, pos.y() - 35, 100, 70, self.current_color)

            if shape:
                self.storage.add(shape)
                self.select_shape(shape)

        self.drag_start = pos
        self.update()

    def mouseMoveEvent(self, event):
        if not self.drag_start or not self.selected_shapes:
            return
        delta = event.pos() - self.drag_start
        for shape in self.selected_shapes:
            shape.move_by(delta.x(), delta.y(), self)
        self.drag_start = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.drag_start = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete and self.selected_shapes:
            for s in list(self.selected_shapes):
                self.storage.remove(s)
            self.deselect_all()
            self.update()
            return

        if not self.selected_shapes:
            return

        step = 10 if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else 1
        dx = dy = 0
        if event.key() == Qt.Key_Left:  dx = -step
        if event.key() == Qt.Key_Right: dx = step
        if event.key() == Qt.Key_Up:    dy = -step
        if event.key() == Qt.Key_Down:  dy = step

        if dx or dy:
            for s in self.selected_shapes:
                s.move_by(dx, dy, self)
            self.update()

    def select_shape(self, shape):
        shape.selected = True
        self.selected_shapes.add(shape)

    def deselect_all(self):
        for s in self.selected_shapes:
            s.selected = False
        self.selected_shapes.clear()

    def toggle_selection(self, shape):
        if shape in self.selected_shapes:
            shape.selected = False
            self.selected_shapes.remove(shape)
        else:
            shape.selected = True
            self.selected_shapes.add(shape)

    def select_all(self):
        self.deselect_all()
        for s in self.storage:
            self.select_shape(s)
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ЛР4 — Круги и прямоугольники")
        self.resize(1100, 750)

        central = QWidget()
        layout = QVBoxLayout(central)
        self.canvas = Canvas()
        layout.addWidget(self.canvas)
        self.setCentralWidget(central)

        self.create_toolbar()
        self.create_menu()

    def create_toolbar(self):
        tb = QToolBar("Инструменты")
        self.addToolBar(tb)

        group = QActionGroup(self)
        group.setExclusive(True)

        circle_act = QAction("Круг", self)
        circle_act.setCheckable(True)
        circle_act.setChecked(True)
        circle_act.triggered.connect(lambda: setattr(self.canvas, "current_shape_type", "circle"))
        group.addAction(circle_act)
        tb.addAction(circle_act)

        rect_act = QAction("Прямоугольник", self)
        rect_act.setCheckable(True)
        rect_act.triggered.connect(lambda: setattr(self.canvas, "current_shape_type", "rectangle"))
        group.addAction(rect_act)
        tb.addAction(rect_act)

        tb.addSeparator()

        color_act = QAction("Цвет", self)
        color_act.triggered.connect(self.choose_color)
        tb.addAction(color_act)

    def create_menu(self):
        menu = self.menuBar()
        edit = menu.addMenu("Правка")
        select_all = QAction("Выделить всё", self)
        select_all.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all.triggered.connect(self.canvas.select_all)
        edit.addAction(select_all)

    def choose_color(self):
        color = QColorDialog.getColor(self.canvas.current_color)
        if color.isValid():
            self.canvas.current_color = color


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec()