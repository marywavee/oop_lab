import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import Qt, QPoint, QRect, QPointF, QLineF

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
    HANDLE_SIZE = 12

    def __init__(self, color=None):
        if isinstance(color, QColor):
            self.color = QColor(color)
        elif isinstance(color, str):
            self.color = QColor(color)
        else:
            self.color = QColor("#000000")
        if not self.color.isValid():
            self.color = QColor("#000000")

        self.selected = False

    def draw(self, p: QPainter):
        raise NotImplementedError

    def bounding_rect(self) -> QRect:
        raise NotImplementedError

    def contains(self, p: QPoint) -> bool:
        raise NotImplementedError

    def move_by(self, dx, dy, canvas) -> bool:
        raise NotImplementedError

    def resize(self, handle_idx, delta, canvas):
        raise NotImplementedError

    def handles(self):
        r = self.bounding_rect()
        c = r.center()
        return [
            r.topLeft(), r.topRight(), r.bottomRight(), r.bottomLeft(),
            QPoint(c.x(), r.top()), QPoint(c.x(), r.bottom()),
            QPoint(r.left(), c.y()), QPoint(r.right(), c.y())
        ]

    def draw_handles(self, painter: QPainter):
        if not self.selected:
            return
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        hs = self.HANDLE_SIZE
        for h in self.handles():
            rect = QRect(h.x() - hs // 2, h.y() - hs // 2, hs, hs)
            painter.drawRect(rect)


class Circle(Shape):
    def __init__(self, center: QPoint, radius: int = 40, color=None):
        super().__init__(color)
        self.center = QPoint(center)
        self.radius = int(radius)

    def draw(self, painter: QPainter):
        pen = QPen(self.color, 3)
        painter.setPen(pen)
        painter.setBrush(QBrush(self.color) if self.selected else QBrush())
        painter.drawEllipse(self.center, self.radius, self.radius)
        self.draw_handles(painter)

    def bounding_rect(self) -> QRect:
        r = self.radius + 10
        return QRect(self.center.x() - r, self.center.y() - r, r * 2, r * 2)

    def contains(self, p: QPoint) -> bool:
        dx = p.x() - self.center.x()
        dy = p.y() - self.center.y()
        return dx * dx + dy * dy <= (self.radius + 10) ** 2

    def move_by(self, dx, dy, canvas) -> bool:
        nr = self.bounding_rect().translated(dx, dy)
        if canvas.rect().contains(nr):
            self.center += QPoint(dx, dy)
            return True
        return False

    def resize(self, idx, delta, canvas):
        h = self.handles()[idx]
        vec = QPointF(h.x() - self.center.x(), h.y() - self.center.y())
        length = (vec.x() ** 2 + vec.y() ** 2) ** 0.5
        if length < 1:
            return
        ux = vec.x() / length
        uy = vec.y() / length
        dr = delta.x() * ux + delta.y() * uy
        new_radius = max(10, int(self.radius + dr))
        nr = QRect(self.center.x() - new_radius - 10,
                   self.center.y() - new_radius - 10,
                   (new_radius + 10) * 2, (new_radius + 10) * 2)
        if canvas.rect().contains(nr):
            self.radius = new_radius


class Rectangle(Shape):
    def __init__(self, x, y, w=100, h=70, color=None):
        super().__init__(color)
        self.rect = QRect(x, y, w, h)

    def draw(self, painter: QPainter):
        painter.setPen(QPen(self.color, 3))
        painter.setBrush(QBrush(self.color) if self.selected else QBrush())
        painter.drawRect(self.rect)
        self.draw_handles(painter)

    def bounding_rect(self) -> QRect:
        return self.rect.adjusted(-10, -10, 10, 10)

    def contains(self, p: QPoint) -> bool:
        return self.rect.adjusted(-10, -10, 10, 10).contains(p)

    def move_by(self, dx, dy, canvas) -> bool:
        nr = self.bounding_rect().translated(dx, dy)
        if canvas.rect().contains(nr):
            self.rect.translate(dx, dy)
            return True
        return False

    def resize(self, idx, delta, canvas):
        r = QRect(self.rect)
        nr = QRect(r)

        if idx == 0:   nr.setTopLeft(r.topLeft() + delta)
        elif idx == 1: nr.setTopRight(r.topRight() + delta)
        elif idx == 2: nr.setBottomRight(r.bottomRight() + delta)
        elif idx == 3: nr.setBottomLeft(r.bottomLeft() + delta)
        elif idx == 4: nr.setTop(r.top() + delta.y())
        elif idx == 5: nr.setBottom(r.bottom() + delta.y())
        elif idx == 6: nr.setLeft(r.left() + delta.x())
        elif idx == 7: nr.setRight(r.right() + delta.x())

        if nr.width() < 20:
            if idx in (0, 3, 6):
                nr.setLeft(nr.right() - 20)
            else:
                nr.setRight(nr.left() + 20)
        if nr.height() < 20:
            if idx in (0, 1, 4):
                nr.setTop(nr.bottom() - 20)
            else:
                nr.setBottom(nr.top() + 20)

        if canvas.rect().contains(nr.adjusted(-10, -10, 10, 10)):
            self.rect = nr


class Triangle(Shape):
    def __init__(self, center: QPoint, size: int = 60, color=None):
        super().__init__(color)
        s = int(size)
        self.points = [
            QPoint(center.x(), center.y() - s),
            QPoint(center.x() - s, center.y() + s),
            QPoint(center.x() + s, center.y() + s)
        ]

    def draw(self, painter: QPainter):
        painter.setPen(QPen(self.color, 3))
        painter.setBrush(QBrush(self.color) if self.selected else QBrush())
        painter.drawPolygon(QPolygon(self.points))
        self.draw_handles(painter)

    def bounding_rect(self) -> QRect:
        return QPolygon(self.points).boundingRect().adjusted(-10, -10, 10, 10)

    def contains(self, p: QPoint) -> bool:
        return QPolygon(self.points).containsPoint(p, Qt.FillRule.OddEvenFill)

    def move_by(self, dx, dy, canvas) -> bool:
        np = [p + QPoint(dx, dy) for p in self.points]
        nr = QPolygon(np).boundingRect().adjusted(-10, -10, 10, 10)
        if canvas.rect().contains(nr):
            self.points = np
            return True
        return False

    def resize(self, idx, delta, canvas):
        old = QPolygon(self.points).boundingRect()
        new = QRect(old)

        if idx == 0:   new.setTopLeft(old.topLeft() + delta)
        elif idx == 1: new.setTopRight(old.topRight() + delta)
        elif idx == 2: new.setBottomRight(old.bottomRight() + delta)
        elif idx == 3: new.setBottomLeft(old.bottomLeft() + delta)
        elif idx == 4: new.setTop(old.top() + delta.y())
        elif idx == 5: new.setBottom(old.bottom() + delta.y())
        elif idx == 6: new.setLeft(old.left() + delta.x())
        elif idx == 7: new.setRight(old.right() + delta.x())

        if new.width() < 30 or new.height() < 30:
            return
        if not canvas.rect().contains(new.adjusted(-10, -10, 10, 10)):
            return

        cx, cy = old.center().x(), old.center().y()
        sx = new.width() / old.width()
        sy = new.height() / old.height()
        offx = new.left() - old.left()
        offy = new.top() - old.top()

        pts = []
        for p in self.points:
            dx = p.x() - cx
            dy = p.y() - cy
            nx = cx + dx * sx + offx
            ny = cy + dy * sy + offy
            pts.append(QPoint(int(nx), int(ny)))

        self.points = pts


class LineSegment(Shape):
    def __init__(self, p1: QPoint, p2: QPoint, color=None):
        super().__init__(color)
        self.p1 = QPoint(p1)
        self.p2 = QPoint(p2)

    def draw(self, painter: QPainter):
        painter.setPen(QPen(self.color, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(self.p1, self.p2)
        self.draw_handles(painter)

    def bounding_rect(self) -> QRect:
        return QRect(self.p1, self.p2).normalized().adjusted(-15, -15, 15, 15)

    def handles(self):
        return [self.p1, self.p2]

    def contains(self, p: QPoint) -> bool:
        return QLineF(self.p1, self.p2).distanceToPoint(p) <= 10

    def move_by(self, dx, dy, canvas) -> bool:
        np1 = self.p1 + QPoint(dx, dy)
        np2 = self.p2 + QPoint(dx, dy)
        nr = QRect(np1, np2).normalized().adjusted(-15, -15, 15, 15)
        if canvas.rect().contains(nr):
            self.p1, self.p2 = np1, np2
            return True
        return False

    def resize(self, idx, delta, canvas):
        old1, old2 = QPoint(self.p1), QPoint(self.p2)
        if idx == 0:
            self.p1 += delta
        else:
            self.p2 += delta
        nr = QRect(self.p1, self.p2).normalized().adjusted(-15, -15, 15, 15)
        if not canvas.rect().contains(nr):
            self.p1, self.p2 = old1, old2


class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.storage = ShapeStorage()
        self.current_color = QColor("#0066ff")
        self.current_shape_type = "circle"
        self.drag_start = None
        self.selected_shapes = set()
        self.resize_handle = -1

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor("#fafafa"))
        for s in self.storage:
            try:
                s.draw(p)
            except:
                pass

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = event.pos()
        hit = None
        handle_idx = None

        for s in reversed(list(self.storage)):
            if s.selected:
                for i, h in enumerate(s.handles()):
                    hs = Shape.HANDLE_SIZE
                    if QRect(h.x() - hs//2, h.y() - hs//2, hs, hs).contains(pos):
                        hit = s
                        handle_idx = i
                        break
                if handle_idx is not None:
                    break
            try:
                if s.contains(pos):
                    hit = s
                    break
            except:
                continue

        ctrl = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)

        if hit:
            if ctrl:
                self.toggle_selection(hit)
            else:
                if hit not in self.selected_shapes:
                    self.deselect_all()
                    self.select_shape(hit)
        else:
            if not ctrl:
                self.deselect_all()
            if self.current_shape_type == "circle":
                shape = Circle(pos, 40, self.current_color)
            elif self.current_shape_type == "rectangle":
                shape = Rectangle(pos.x()-50, pos.y()-35, 100, 70, self.current_color)
            elif self.current_shape_type == "triangle":
                shape = Triangle(pos, 60, self.current_color)
            else:
                shape = LineSegment(QPoint(pos.x()-60, pos.y()), QPoint(pos.x()+60, pos.y()), self.current_color)
            self.storage.add(shape)
            self.select_shape(shape)

        self.drag_start = pos
        self.resize_handle = handle_idx if handle_idx is not None else -1
        self.update()

    def mouseMoveEvent(self, event):
        if self.drag_start is None:
            return

        delta = event.pos() - self.drag_start

        if self.resize_handle != -1:
            for shape in list(self.selected_shapes):
                try:
                    shape.resize(self.resize_handle, delta, self)
                except:
                    pass
        else:
            for shape in list(self.selected_shapes):
                try:
                    shape.move_by(delta.x(), delta.y(), self)
                except:
                    pass

        self.drag_start = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.drag_start = None
        self.resize_handle = -1

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete and self.selected_shapes:
            for s in list(self.selected_shapes):
                self.storage.remove(s)
            self.deselect_all()
            self.update()
            return

        if not self.selected_shapes:
            return

        step = 10 if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else 1
        dx = dy = 0

        if event.key() == Qt.Key.Key_Left: dx = -step
        elif event.key() == Qt.Key.Key_Right: dx = step
        elif event.key() == Qt.Key.Key_Up: dy = -step
        elif event.key() == Qt.Key.Key_Down: dy = step

        if dx or dy:
            for s in list(self.selected_shapes):
                try:
                    s.move_by(dx, dy, self)
                except:
                    pass
            self.update()

    def select_shape(self, shape):
        shape.selected = True
        self.selected_shapes.add(shape)

    def deselect_all(self):
        for s in list(self.selected_shapes):
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
        self.setWindowTitle("mainWindow")
        self.resize(1200, 800)
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
        tools = [("circle", "Круг"), ("rectangle", "Прямоугольник"),
                 ("triangle", "Треугольник"), ("line", "Отрезок")]
        for name, text in tools:
            act = QAction(text, self)
            act.setCheckable(True)
            if name == "circle":
                act.setChecked(True)
            act.triggered.connect(lambda checked, n=name: setattr(self.canvas, "current_shape_type", n))
            group.addAction(act)
            tb.addAction(act)
        tb.addSeparator()
        color_act = QAction("Цвет", self)
        color_act.triggered.connect(self.choose_color)
        tb.addAction(color_act)

    def create_menu(self):
        menu = self.menuBar()
        edit = menu.addMenu("Navigate")
        a = QAction("Выделить всё", self)
        a.setShortcut(QKeySequence.StandardKey.SelectAll)
        a.triggered.connect(self.canvas.select_all)
        edit.addAction(a)

    def choose_color(self):
        try:
            c = QColorDialog.getColor(self.canvas.current_color, self, "Выбор цвета")
            if not c.isValid():
                return
            nc = QColor(c)
            self.canvas.current_color = QColor(nc)
            for s in list(self.canvas.selected_shapes):
                try:
                    s.color = QColor(nc)
                except:
                    pass
            self.canvas.update()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec()
