import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import Qt, QPoint, QRect, QPointF, QLineF

#
class ShapeFactory:
    _registry = {}

    @classmethod
    def register(cls, name):
        def deco(klass):
            cls._registry[name] = klass
            klass._factory_name = name
            return klass
        return deco

    @classmethod
    def create_from_file(cls, reader):
        line = reader.readline()
        if not line:
            return None
        if not line.strip().startswith("TYPE "):
            raise ValueError("Expected TYPE line")
        typ = line.strip().split(None, 1)[1]
        klass = cls._registry.get(typ)
        if not klass:
            raise ValueError(f"Unknown type: {typ}")
        return klass.load_from_file(reader)


class Shape:
    HANDLE_SIZE = 12

    def __init__(self, color=None):
        self.color = QColor(color) if color else QColor("#000000")
        if not self.color.isValid():
            self.color = QColor("#000000")
        self.selected = False

    # Виртуальные методы
    def draw(self, p: QPainter): raise NotImplementedError
    def bounding_rect(self) -> QRect: raise NotImplementedError
    def contains(self, p: QPoint) -> bool: raise NotImplementedError
    def move_by(self, dx: int, dy: int, canvas) -> bool: raise NotImplementedError
    def resize(self, handle_idx: int, delta: QPoint, canvas): raise NotImplementedError
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

    # Сериализация
    def save_to_file(self, writer): raise NotImplementedError
    @classmethod
    def load_from_file(cls, reader): raise NotImplementedError


# ====================== Примитивы ======================
@ShapeFactory.register('Circle')
class Circle(Shape):
    def __init__(self, center: QPoint, radius: int = 40, color=None):
        super().__init__(color)
        self.center = QPoint(center)
        self.radius = max(10, int(radius))

    def draw(self, p: QPainter):
        p.setPen(QPen(self.color, 3))
        p.setBrush(QBrush(self.color) if self.selected else QBrush())
        p.drawEllipse(self.center, self.radius, self.radius)
        self.draw_handles(p)

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
        length = (vec.x()**2 + vec.y()**2)**0.5
        if length < 1: return
        ux = vec.x() / length
        uy = vec.y() / length
        dr = delta.x() * ux + delta.y() * uy
        new_r = max(10, int(self.radius + dr))
        nr = QRect(self.center.x() - new_r - 10, self.center.y() - new_r - 10,
                   (new_r + 10) * 2, (new_r + 10) * 2)
        if canvas.rect().contains(nr):
            self.radius = new_r

    def save_to_file(self, writer):
        writer.write('TYPE Circle\n')
        writer.write(f'CENTER {self.center.x()} {self.center.y()}\n')
        writer.write(f'RADIUS {self.radius}\n')
        writer.write(f'COLOR {self.color.name()}\n')

    @classmethod
    def load_from_file(cls, reader):
        cx = cy = 0
        radius = 40
        color = "#000000"
        while True:
            line = reader.readline()
            if not line or line.strip() == "END_OBJECT":
                break
            line = line.strip()
            if line.startswith("CENTER "):
                _, x, y = line.split()
                cx, cy = int(x), int(y)
            elif line.startswith("RADIUS "):
                radius = int(line.split()[1])
            elif line.startswith("COLOR "):
                color = line.split()[1]
        return Circle(QPoint(cx, cy), radius, color)


@ShapeFactory.register('Rectangle')
class Rectangle(Shape):
    def __init__(self, x, y, w=100, h=70, color=None):
        super().__init__(color)
        self.rect = QRect(x, y, max(20, w), max(20, h)).normalized()

    def draw(self, p: QPainter):
        p.setPen(QPen(self.color, 3))
        p.setBrush(QBrush(self.color) if self.selected else QBrush())
        p.drawRect(self.rect)
        self.draw_handles(p)

    def bounding_rect(self) -> QRect:
        return self.rect.adjusted(-10, -10, 10, 10)

    def contains(self, p: QPoint) -> bool:
        return self.bounding_rect().contains(p)

    def move_by(self, dx, dy, canvas) -> bool:
        nr = self.bounding_rect().translated(dx, dy)
        if canvas.rect().contains(nr):
            self.rect.translate(dx, dy)
            return True
        return False

    def resize(self, idx, delta, canvas):
        r = QRect(self.rect)
        if idx == 0: r.setTopLeft(r.topLeft() + delta)
        elif idx == 1: r.setTopRight(r.topRight() + delta)
        elif idx == 2: r.setBottomRight(r.bottomRight() + delta)
        elif idx == 3: r.setBottomLeft(r.bottomLeft() + delta)
        elif idx == 4: r.setTop(r.top() + delta.y())
        elif idx == 5: r.setBottom(r.bottom() + delta.y())
        elif idx == 6: r.setLeft(r.left() + delta.x())
        elif idx == 7: r.setRight(r.right() + delta.x())
        if r.width() < 20: r.setWidth(20)
        if r.height() < 20: r.setHeight(20)
        if canvas.rect().contains(r.adjusted(-10, -10, 10, 10)):
            self.rect = r.normalized()

    def save_to_file(self, writer):
        writer.write('TYPE Rectangle\n')
        writer.write(f'RECT {self.rect.x()} {self.rect.y()} {self.rect.width()} {self.rect.height()}\n')
        writer.write(f'COLOR {self.color.name()}\n')

    @classmethod
    def load_from_file(cls, reader):
        x = y = w = h = 0
        color = "#000000"
        while True:
            line = reader.readline()
            if not line or line.strip() == "END_OBJECT":
                break
            line = line.strip()
            if line.startswith("RECT "):
                parts = line.split()[1:]
                x, y, w, h = map(int, parts)
            elif line.startswith("COLOR "):
                color = line.split()[1]
        return Rectangle(x, y, w, h, color)


@ShapeFactory.register('Triangle')
class Triangle(Shape):
    def __init__(self, center: QPoint, size: int = 60, color=None):
        super().__init__(color)
        s = int(size)
        self.points = [
            QPoint(center.x(), center.y() - s),
            QPoint(center.x() - s, center.y() + s),
            QPoint(center.x() + s, center.y() + s)
        ]

    def draw(self, p: QPainter):
        p.setPen(QPen(self.color, 3))
        p.setBrush(QBrush(self.color) if self.selected else QBrush())
        p.drawPolygon(QPolygon(self.points))
        self.draw_handles(p)

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
        if idx == 0: new.setTopLeft(old.topLeft() + delta)
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
        ox = new.left() - old.left()
        oy = new.top() - old.top()
        self.points = [
            QPoint(int(cx + (p.x() - cx) * sx + ox), int(cy + (p.y() - cy) * sy + oy))
            for p in self.points
        ]

    def save_to_file(self, writer):
        writer.write('TYPE Triangle\n')
        for i, pt in enumerate(self.points, 1):
            writer.write(f'P{i} {pt.x()} {pt.y()}\n')
        writer.write(f'COLOR {self.color.name()}\n')

    @classmethod
    def load_from_file(cls, reader):
        pts = [(0, 0)] * 3
        color = "#000000"
        while True:
            line = reader.readline()
            if not line or line.strip() == "END_OBJECT":
                break
            line = line.strip()
            if line.startswith("P1 "): pts[0] = tuple(map(int, line.split()[1:]))
            elif line.startswith("P2 "): pts[1] = tuple(map(int, line.split()[1:]))
            elif line.startswith("P3 "): pts[2] = tuple(map(int, line.split()[1:]))
            elif line.startswith("COLOR "): color = line.split()[1]
        center = QPoint(sum(x for x, y in pts)//3, sum(y for x, y in pts)//3)
        t = Triangle(center, 60, color)
        t.points = [QPoint(x, y) for x, y in pts]
        return t


@ShapeFactory.register('LineSegment')
class LineSegment(Shape):
    def __init__(self, p1: QPoint, p2: QPoint, color=None):
        super().__init__(color)
        self.p1 = QPoint(p1)
        self.p2 = QPoint(p2)

    def draw(self, p: QPainter):
        p.setPen(QPen(self.color, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(self.p1, self.p2)
        self.draw_handles(p)

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
        if idx == 0:
            self.p1 += delta
        else:
            self.p2 += delta
        nr = QRect(self.p1, self.p2).normalized().adjusted(-15, -15, 15, 15)
        if not canvas.rect().contains(nr):
            self.p1 -= delta if idx == 0 else QPoint(0, 0)
            self.p2 -= delta if idx == 1 else QPoint(0, 0)

    def save_to_file(self, writer):
        writer.write('TYPE LineSegment\n')
        writer.write(f'P1 {self.p1.x()} {self.p1.y()}\n')
        writer.write(f'P2 {self.p2.x()} {self.p2.y()}\n')
        writer.write(f'COLOR {self.color.name()}\n')

    @classmethod
    def load_from_file(cls, reader):
        p1 = p2 = (0, 0)
        color = "#000000"
        while True:
            line = reader.readline()
            if not line or line.strip() == "END_OBJECT":
                break
            line = line.strip()
            if line.startswith("P1 "): p1 = tuple(map(int, line.split()[1:]))
            if line.startswith("P2 "): p2 = tuple(map(int, line.split()[1:]))
            if line.startswith("COLOR "): color = line.split()[1]
        return LineSegment(QPoint(*p1), QPoint(*p2), color)



@ShapeFactory.register('Group')
class Group(Shape):
    def __init__(self, items=None):
        super().__init__(None)
        self.items = list(items) if items else []

    def draw(self, p: QPainter):
        for item in self.items:
            item.draw(p)
        if self.selected:
            r = self.bounding_rect()
            if not r.isEmpty():
                pen = QPen(Qt.GlobalColor.darkGray, 2, Qt.PenStyle.DashLine)
                p.setPen(pen)
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawRect(r)
                self.draw_handles(p)

    def bounding_rect(self) -> QRect:
        if not self.items:
            return QRect()
        r = self.items[0].bounding_rect()
        for it in self.items[1:]:
            r = r.united(it.bounding_rect())
        return r

    def contains(self, p: QPoint) -> bool:
        return any(it.contains(p) for it in self.items)

    def move_by(self, dx, dy, canvas) -> bool:
        nr = self.bounding_rect().translated(dx, dy)
        if not canvas.rect().contains(nr):
            return False
        for it in self.items:
            it.move_by(dx, dy, canvas)
        return True

    def _apply_transform(self, sx, sy, ox, oy, cx, cy):
        """Аффинное преобразование всех дочерних объектов"""
        for it in self.items:
            if isinstance(it, Circle):
                dx = it.center.x() - cx
                dy = it.center.y() - cy
                it.center = QPoint(int(cx + dx * sx + ox), int(cy + dy * sy + oy))
                it.radius = max(10, int(it.radius * (sx + sy) * 0.5))

            elif isinstance(it, Rectangle):
                pts = [it.rect.topLeft(), it.rect.topRight(),
                       it.rect.bottomRight(), it.rect.bottomLeft()]
                new_pts = [QPoint(int(cx + (p.x() - cx) * sx + ox),
                                  int(cy + (p.y() - cy) * sy + oy)) for p in pts]
                new_r = QRect(new_pts[0], new_pts[2]).normalized()
                new_r.setWidth(max(20, new_r.width()))
                new_r.setHeight(max(20, new_r.height()))
                it.rect = new_r

            elif isinstance(it, Triangle):
                it.points = [QPoint(int(cx + (p.x() - cx) * sx + ox),
                                   int(cy + (p.y() - cy) * sy + oy)) for p in it.points]

            elif isinstance(it, LineSegment):
                it.p1 = QPoint(int(cx + (it.p1.x() - cx) * sx + ox),
                              int(cy + (it.p1.y() - cy) * sy + oy))
                it.p2 = QPoint(int(cx + (it.p2.x() - cx) * sx + ox),
                              int(cy + (it.p2.y() - cy) * sy + oy))

            elif isinstance(it, Group):
                it._apply_transform(sx, sy, ox, oy, cx, cy)

    def resize(self, idx, delta, canvas):
        """Изменение размера группы с сохранением пропорций детей"""
        old_bounds = self.bounding_rect()
        if old_bounds.width() < 30 or old_bounds.height() < 30:
            return

        new_bounds = QRect(old_bounds)

        # Изменяем границы в зависимости от выбранного хендла
        if idx == 0:  # top-left
            new_bounds.setTopLeft(old_bounds.topLeft() + delta)
        elif idx == 1:  # top-right
            new_bounds.setTopRight(old_bounds.topRight() + delta)
        elif idx == 2:  # bottom-right
            new_bounds.setBottomRight(old_bounds.bottomRight() + delta)
        elif idx == 3:  # bottom-left
            new_bounds.setBottomLeft(old_bounds.bottomLeft() + delta)
        elif idx == 4:  # top
            new_bounds.setTop(old_bounds.top() + delta.y())
        elif idx == 5:  # bottom
            new_bounds.setBottom(old_bounds.bottom() + delta.y())
        elif idx == 6:  # left
            new_bounds.setLeft(old_bounds.left() + delta.x())
        elif idx == 7:  # right
            new_bounds.setRight(old_bounds.right() + delta.x())

        # Проверяем минимальный размер
        if new_bounds.width() < 30 or new_bounds.height() < 30:
            return

        # Проверяем, чтобы группа не вышла за границы канваса
        if not canvas.rect().contains(new_bounds):
            return

        # Вычисляем масштаб по осям
        scale_x = new_bounds.width() / old_bounds.width()
        scale_y = new_bounds.height() / old_bounds.height()

        # Вычисляем смещение
        offset_x = new_bounds.left() - old_bounds.left()
        offset_y = new_bounds.top() - old_bounds.top()

        # Центр для масштабирования
        center_x = old_bounds.center().x()
        center_y = old_bounds.center().y()

        # Применяем преобразование к каждому объекту
        for item in self.items:
            if isinstance(item, Circle):
                # Масштабируем относительно центра группы
                new_x = center_x + (item.center.x() - center_x) * scale_x + offset_x
                new_y = center_y + (item.center.y() - center_y) * scale_y + offset_y
                item.center = QPoint(int(new_x), int(new_y))
                # Средний масштаб для радиуса
                avg_scale = (scale_x + scale_y) / 2
                item.radius = max(10, int(item.radius * avg_scale))

            elif isinstance(item, Rectangle):
                # Для прямоугольника масштабируем каждую точку
                new_left = center_x + (item.rect.left() - center_x) * scale_x + offset_x
                new_top = center_y + (item.rect.top() - center_y) * scale_y + offset_y
                new_right = center_x + (item.rect.right() - center_x) * scale_x + offset_x
                new_bottom = center_y + (item.rect.bottom() - center_y) * scale_y + offset_y

                new_rect = QRect(
                    int(new_left), int(new_top),
                    int(new_right - new_left), int(new_bottom - new_top)
                )

                # Гарантируем минимальный размер
                if new_rect.width() < 20:
                    new_rect.setWidth(20)
                if new_rect.height() < 20:
                    new_rect.setHeight(20)

                item.rect = new_rect

            elif isinstance(item, Triangle):
                # Масштабируем каждую точку треугольника
                new_points = []
                for point in item.points:
                    new_x = center_x + (point.x() - center_x) * scale_x + offset_x
                    new_y = center_y + (point.y() - center_y) * scale_y + offset_y
                    new_points.append(QPoint(int(new_x), int(new_y)))
                item.points = new_points

            elif isinstance(item, LineSegment):
                # Масштабируем концы отрезка
                new_p1_x = center_x + (item.p1.x() - center_x) * scale_x + offset_x
                new_p1_y = center_y + (item.p1.y() - center_y) * scale_y + offset_y
                new_p2_x = center_x + (item.p2.x() - center_x) * scale_x + offset_x
                new_p2_y = center_y + (item.p2.y() - center_y) * scale_y + offset_y

                item.p1 = QPoint(int(new_p1_x), int(new_p1_y))
                item.p2 = QPoint(int(new_p2_x), int(new_p2_y))

            elif isinstance(item, Group):
                # Для вложенной группы рекурсивно применяем тот же метод
                item.resize(idx, delta, canvas)

    def save_to_file(self, writer):
        writer.write('TYPE Group\n')
        writer.write(f'CHILD_COUNT {len(self.items)}\n')
        for it in self.items:
            it.save_to_file(writer)
            writer.write('END_OBJECT\n')

    @classmethod
    def load_from_file(cls, reader):
        child_count = 0
        while True:
            line = reader.readline()
            if not line:
                break
            line = line.strip()
            if line.startswith('CHILD_COUNT '):
                child_count = int(line.split()[1])
                break
        items = []
        for _ in range(child_count):
            obj = ShapeFactory.create_from_file(reader)
            if obj:
                items.append(obj)
            while True:
                line = reader.readline()
                if not line or line.strip() == 'END_OBJECT':
                    break
        return Group(items)


# ====================== Хранилище ======================
class ShapeStorage:
    def __init__(self):
        self._items = []

    def add(self, shape): self._items.append(shape)
    def remove(self, shape):
        if shape in self._items:
            self._items.remove(shape)
    def clear(self): self._items.clear()
    def __iter__(self): return iter(self._items)
    def __len__(self): return len(self._items)



class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.storage = ShapeStorage()
        self.current_color = QColor("#0066ff")
        self.current_shape_type = "circle"
        self.drag_start = None
        self.selected_shapes = []
        self.resize_handle = -1

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor("#fafafa"))
        for s in self.storage:
            s.draw(p)

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = event.pos()
        hit = None
        handle_idx = -1
        for s in reversed(list(self.storage)):
            if s.selected:
                for i, h in enumerate(s.handles()):
                    if QRect(h.x() - 6, h.y() - 6, 12, 12).contains(pos):
                        hit = s
                        handle_idx = i
                        break
                if handle_idx != -1: break
            if s.contains(pos):
                hit = s
                break

        ctrl = event.modifiers() & Qt.KeyboardModifier.ControlModifier
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
        self.resize_handle = handle_idx
        self.update()

    def mouseMoveEvent(self, event):
        if not self.drag_start: return
        delta = event.pos() - self.drag_start
        if self.resize_handle != -1:
            for s in self.selected_shapes:
                s.resize(self.resize_handle, delta, self)
        else:
            for s in self.selected_shapes:
                s.move_by(delta.x(), delta.y(), self)
        self.drag_start = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.drag_start = None
        self.resize_handle = -1

    def keyPressEvent(self, event):
        # Ctrl+A - выделить все
        if event.matches(QKeySequence.StandardKey.SelectAll):
            self.select_all()
            return

        if event.key() == Qt.Key.Key_Delete and self.selected_shapes:
            for s in list(self.selected_shapes):
                self.storage.remove(s)
            self.deselect_all()
            self.update()
            return

        step = 10 if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else 1
        dx = dy = 0
        if event.key() == Qt.Key.Key_Left: dx = -step
        elif event.key() == Qt.Key.Key_Right: dx = step
        elif event.key() == Qt.Key.Key_Up: dy = -step
        elif event.key() == Qt.Key.Key_Down: dy = step
        if dx or dy:
            for s in self.selected_shapes:
                s.move_by(dx, dy, self)
            self.update()

    def select_all(self):
        self.deselect_all()
        for s in self.storage:
            self.select_shape(s)
        self.update()

    def select_shape(self, s):
        s.selected = True
        if s not in self.selected_shapes:
            self.selected_shapes.append(s)

    def deselect_all(self):
        for s in self.selected_shapes:
            s.selected = False
        self.selected_shapes.clear()

    def toggle_selection(self, s):
        if s in self.selected_shapes:
            s.selected = False
            self.selected_shapes.remove(s)
        else:
            s.selected = True
            self.selected_shapes.append(s)

    def group_selected(self):
        if len(self.selected_shapes) < 2: return
        items = list(self.selected_shapes)
        for it in items:
            self.storage.remove(it)
            it.selected = False
        g = Group(items)
        self.storage.add(g)
        self.deselect_all()
        self.select_shape(g)
        self.update()

    def ungroup_selected(self):
        to_add = []
        to_remove = []
        for s in self.selected_shapes:
            if isinstance(s, Group):
                to_remove.append(s)
                to_add.extend(s.items)
        for g in to_remove:
            self.storage.remove(g)
        for it in to_add:
            self.storage.add(it)
        self.deselect_all()
        self.update()

    def save_to_file(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f'OBJECT_COUNT {len(self.storage)}\n')
            for it in self.storage:
                it.save_to_file(f)
                f.write('END_OBJECT\n')

    def load_from_file(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            header = f.readline().strip()
            if not header.startswith('OBJECT_COUNT'):
                return
            count = int(header.split()[1])
            self.storage.clear()
            for _ in range(count):
                obj = ShapeFactory.create_from_file(f)
                if obj:
                    self.storage.add(obj)
                while True:
                    line = f.readline()
                    if not line or line.strip() == 'END_OBJECT':
                        break
        self.deselect_all()
        self.update()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ЛР6 — Группировка и сохранение")
        self.resize(1200, 800)
        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)

        tb = self.addToolBar("Инструменты")
        group = QActionGroup(self)
        group.setExclusive(True)
        for name, text in [("circle", "Круг"), ("rectangle", "Прямоугольник"),
                           ("triangle", "Треугольник"), ("line", "Отрезок")]:
            a = QAction(text, self)
            a.setCheckable(True)
            if name == "circle": a.setChecked(True)
            a.triggered.connect(lambda checked, n=name: setattr(self.canvas, "current_shape_type", n))
            group.addAction(a)
            tb.addAction(a)

        tb.addSeparator()
        tb.addAction(QAction("Группировать (Ctrl+G)", self, triggered=self.canvas.group_selected,
                             shortcut="Ctrl+G"))
        tb.addAction(QAction("Разгруппировать (Ctrl+Shift+G)", self, triggered=self.canvas.ungroup_selected,
                             shortcut="Ctrl+Shift+G"))
        tb.addSeparator()
        tb.addAction(QAction("Цвет", self, triggered=self.choose_color))

        menu = self.menuBar()
        file = menu.addMenu("Файл")
        file.addAction(QAction("Сохранить...", self, shortcut="Ctrl+S", triggered=self.save))
        file.addAction(QAction("Загрузить...", self, shortcut="Ctrl+O", triggered=self.load))

    def choose_color(self):
        c = QColorDialog.getColor(self.canvas.current_color, self)
        if c.isValid():
            self.canvas.current_color = c
            for s in self.canvas.selected_shapes:
                s.color = QColor(c)
            self.canvas.update()

    def save(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить", "", "Text Files (*.txt)")
        if path:
            self.canvas.save_to_file(path)

    def load(self):
        path, _ = QFileDialog.getOpenFileName(self, "Загрузить", "", "Text Files (*.txt)")
        if path:
            self.canvas.load_from_file(path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec()