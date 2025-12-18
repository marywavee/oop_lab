import sys
import json
import math
import uuid
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from PyQt6.QtGui import QPainter, QColor, QAction, QBrush, QPen
from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QColorDialog,
                             QToolBar, QTreeView, QFileDialog, QSplitter)
from PyQt6.QtCore import Qt, QAbstractItemModel, QModelIndex, pyqtSignal, QObject, QPointF


class Subject(QObject):
    changed = pyqtSignal()
    def notify(self):
        self.changed.emit()


class Component(ABC):
    def __init__(self):
        self._id = str(uuid.uuid4())
        self._is_selected = False

    @property
    def id(self):
        return self._id

    @property
    def is_selected(self) -> bool:
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value: bool):
        self._is_selected = value

    @abstractmethod
    def draw(self, painter: QPainter): pass
    @abstractmethod
    def contains(self, point) -> bool: pass
    @abstractmethod
    def move(self, dx: float, dy: float, form_width: float, form_height: float) -> bool: pass
    @abstractmethod
    def resize_shape(self, dw: float, dh: float, form_width: float, form_height: float) -> bool: pass
    @abstractmethod
    def adjust_to_bounds(self, form_width: float, form_height: float): pass
    @abstractmethod
    def get_bounding_rect(self) -> tuple: pass
    @abstractmethod
    def save(self) -> Dict[str, Any]: pass
    @abstractmethod
    def load(self, data: Dict[str, Any]): pass
    @abstractmethod
    def get_children(self) -> List['Component']: pass
    @abstractmethod
    def get_type_name(self) -> str: pass
    @abstractmethod
    def set_color(self, color: QColor): pass

    @property
    @abstractmethod
    def x(self): pass
    @property
    @abstractmethod
    def y(self): pass
    @property
    @abstractmethod
    def width(self): pass
    @property
    @abstractmethod
    def height(self): pass


class Shape(Component):
    def __init__(self, x, y):
        super().__init__()
        self._x = x
        self._y = y
        self._width = 60
        self._height = 60
        self._color = QColor(0, 0, 255)
        self.selection_color = QColor(255, 0, 0)

    @property
    def x(self): return self._x
    @x.setter
    def x(self, value): self._x = value
    @property
    def y(self): return self._y
    @y.setter
    def y(self, value): self._y = value
    @property
    def width(self): return self._width
    @width.setter
    def width(self, value):
        if value > 0: self._width = value
    @property
    def height(self): return self._height
    @height.setter
    def height(self, value):
        if value > 0: self._height = value

    def set_color(self, color: QColor):
        self._color = color

    def move(self, dx, dy, form_width, form_height):
        new_x = self._x + dx
        new_y = self._y + dy
        if 0 <= new_x <= form_width - self._width and 0 <= new_y <= form_height - self._height:
            self._x = new_x
            self._y = new_y
            return True
        return False

    def resize_shape(self, dw, dh, form_width, form_height):
        new_width = max(20, self._width + dw)
        new_height = max(20, self._height + dh)
        if self._x + new_width <= form_width and self._y + new_height <= form_height:
            self._width = new_width
            self._height = new_height
            return True
        return False

    def adjust_to_bounds(self, form_width, form_height):
        if self._x < 0: self._x = 0
        if self._y < 0: self._y = 0
        if self._x + self._width > form_width:
            self._x = max(0, form_width - self._width)
        if self._y + self._height > form_height:
            self._y = max(0, form_height - self._height)

    def get_bounding_rect(self):
        return (self._x, self._y, self._width, self._height)

    def get_children(self) -> List[Component]:
        return []

    def get_type_name(self) -> str:
        return type(self).__name__.lower()

    def save(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.get_type_name(),
            'x': self._x,
            'y': self._y,
            'width': self._width,
            'height': self._height,
            'color': self._color.name(),
            'is_selected': self.is_selected
        }

    def load(self, data: Dict[str, Any]):
        self._id = data.get('id', self._id)
        self._x = data['x']
        self._y = data['y']
        self._width = data['width']
        self._height = data['height']
        self._color = QColor(data['color'])
        self.is_selected = data['is_selected']


class Circle(Shape):
    def draw(self, painter):
        painter.setPen(QPen(self._color, 2))
        painter.drawEllipse(int(self.x), int(self.y), int(self.width), int(self.height))
        if self.is_selected:
            painter.setPen(QPen(self.selection_color, 2, Qt.PenStyle.DashLine))
            painter.drawEllipse(int(self.x - 3), int(self.y - 3), int(self.width + 6), int(self.height + 6))

    def contains(self, point):
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        r = min(self.width, self.height) / 2
        return math.hypot(point.x() - cx, point.y() - cy) <= r


class Rectangle(Shape):
    def __init__(self, x, y):
        super().__init__(x, y)
        self._width = 80
        self._height = 50

    def draw(self, painter):
        painter.setPen(QPen(self._color, 2))
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
        if self.is_selected:
            painter.setPen(QPen(self.selection_color, 2, Qt.PenStyle.DashLine))
            painter.drawRect(int(self.x - 3), int(self.y - 3), int(self.width + 6), int(self.height + 6))

    def contains(self, point):
        return self.x <= point.x() <= self.x + self.width and self.y <= point.y() <= self.y + self.height


class Triangle(Shape):
    def __init__(self, x, y):
        super().__init__(x, y)
        self._width = 70
        self._height = 70

    def draw(self, painter):
        points = [
            QPointF(self.x + self.width / 2, self.y),
            QPointF(self.x, self.y + self.height),
            QPointF(self.x + self.width, self.y + self.height)
        ]
        painter.setPen(QPen(self._color, 2))
        painter.drawPolygon(points)
        if self.is_selected:
            painter.setPen(QPen(self.selection_color, 2, Qt.PenStyle.DashLine))
            painter.drawRect(int(self.x - 3), int(self.y - 3), int(self.width + 6), int(self.height + 6))

    def contains(self, point):
        x, y = point.x(), point.y()
        x1, y1 = self.x + self.width / 2, self.y
        x2, y2 = self.x, self.y + self.height
        x3, y3 = self.x + self.width, self.y + self.height

        def sign(p1x, p1y, p2x, p2y, p3x, p3y):
            return (p1x - p3x) * (p2y - p3y) - (p2x - p3x) * (p1y - p3y)

        d1 = sign(x, y, x1, y1, x2, y2)
        d2 = sign(x, y, x2, y2, x3, y3)
        d3 = sign(x, y, x3, y3, x1, y1)
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        return not (has_neg and has_pos)


class Line(Shape):
    def __init__(self, x, y):
        super().__init__(x, y)
        self._width = 100
        self._height = 5

    def draw(self, painter):
        painter.setPen(QPen(self._color, int(self.height)))
        painter.drawLine(int(self.x), int(self.y), int(self.x + self.width), int(self.y))
        if self.is_selected:
            painter.setPen(QPen(QColor(0, 255, 0), 3, Qt.PenStyle.DashLine))
            painter.drawRect(int(self.x - 5), int(self.y - 10), int(self.width + 10), 20)

    def contains(self, point):
        x1 = self.x
        x2 = self.x + self.width
        y1 = self.y
        if min(x1, x2) - 10 <= point.x() <= max(x1, x2) + 10 and abs(point.y() - y1) <= 15:
            return True
        return False


class Arrow(Component):
    def __init__(self, source: Component, target: Component):
        super().__init__()
        self.source = source
        self.target = target
        self.color = QColor(255, 0, 0)
        self.selection_color = QColor(255, 165, 0)
        self._saved_source_id = None
        self._saved_target_id = None

    @property
    def x(self): return self.get_bounding_rect()[0]
    @property
    def y(self): return self.get_bounding_rect()[1]
    @property
    def width(self): return self.get_bounding_rect()[2]
    @property
    def height(self): return self.get_bounding_rect()[3]

    def draw(self, painter: QPainter):
        if not self.source or not self.target: return
        painter.save()
        try:
            src = self.source.get_bounding_rect()
            tgt = self.target.get_bounding_rect()
            src_x = src[0] + src[2] / 2
            src_y = src[1] + src[3] / 2
            tgt_x = tgt[0] + tgt[2] / 2
            tgt_y = tgt[1] + tgt[3] / 2
            pen = QPen(self.color, 3)
            painter.setPen(pen)
            painter.drawLine(QPointF(src_x, src_y), QPointF(tgt_x, tgt_y))
            angle = math.atan2(tgt_y - src_y, tgt_x - src_x)
            arrow_size = 15
            p2 = QPointF(tgt_x - arrow_size * math.cos(angle - math.pi / 6), tgt_y - arrow_size * math.sin(angle - math.pi / 6))
            p3 = QPointF(tgt_x - arrow_size * math.cos(angle + math.pi / 6), tgt_y - arrow_size * math.sin(angle + math.pi / 6))
            painter.setBrush(QBrush(self.color))
            painter.drawPolygon([QPointF(tgt_x, tgt_y), p2, p3])
            if self.is_selected:
                painter.setPen(QPen(self.selection_color, 2, Qt.PenStyle.DashLine))
                painter.drawLine(QPointF(src_x, src_y), QPointF(tgt_x, tgt_y))
        finally:
            painter.restore()

    def contains(self, point) -> bool:
        if not self.source or not self.target: return False
        src = self.source.get_bounding_rect()
        tgt = self.target.get_bounding_rect()
        src_x = src[0] + src[2] / 2
        src_y = src[1] + src[3] / 2
        tgt_x = tgt[0] + tgt[2] / 2
        tgt_y = tgt[1] + tgt[3] / 2
        px, py = point.x(), point.y()
        line_len = math.sqrt((tgt_x - src_x)**2 + (tgt_y - src_y)**2)
        if line_len == 0: return False
        u = ((px - src_x) * (tgt_x - src_x) + (py - src_y) * (tgt_y - src_y)) / (line_len ** 2)
        if u < 0 or u > 1: return False
        ix = src_x + u * (tgt_x - src_x)
        iy = src_y + u * (tgt_y - src_y)
        return math.sqrt((px - ix)**2 + (py - iy)**2) < 5

    def move(self, dx, dy, fw, fh): return False
    def resize_shape(self, dw, dh, fw, fh): return False
    def adjust_to_bounds(self, fw, fh): pass
    def get_bounding_rect(self):
        if not self.source or not self.target: return (0, 0, 0, 0)
        src = self.source.get_bounding_rect()
        tgt = self.target.get_bounding_rect()
        min_x = min(src[0], tgt[0])
        min_y = min(src[1], tgt[1])
        max_x = max(src[0] + src[2], tgt[0] + tgt[2])
        max_y = max(src[1] + src[3], tgt[1] + tgt[3])
        return (min_x, min_y, max_x - min_x, max_y - min_y)

    def get_children(self): return []
    def get_type_name(self): return 'arrow'
    def set_color(self, color: QColor): self.color = color

    def save(self):
        return {
            'type': 'arrow',
            'id': self.id,
            'is_selected': self.is_selected,
            'color': self.color.name(),
            'source_id': self.source.id,
            'target_id': self.target.id
        }

    def load(self, data):
        self._id = data.get('id', self._id)
        self.is_selected = data['is_selected']
        self.color = QColor(data['color'])
        self._saved_source_id = data['source_id']
        self._saved_target_id = data['target_id']


class Group(Component):
    def __init__(self):
        super().__init__()
        self._children: List[Component] = []
        self._x = self._y = self._width = self._height = 0
        self.selection_color = QColor(255, 255, 0)

    @property
    def x(self): return self._x
    @property
    def y(self): return self._y
    @property
    def width(self): return self._width
    @property
    def height(self): return self._height

    def _update_bounds(self):
        if not self._children:
            self._x = self._y = self._width = self._height = 0
            return
        min_x = min(c.x for c in self._children)
        min_y = min(c.y for c in self._children)
        max_x = max(c.x + c.width for c in self._children)
        max_y = max(c.y + c.height for c in self._children)
        self._x = min_x
        self._y = min_y
        self._width = max_x - min_x
        self._height = max_y - min_y

    def add(self, component: Component):
        self._children.append(component)
        self._update_bounds()

    def draw(self, painter):
        for child in self._children:
            child.draw(painter)
        if self.is_selected:
            painter.setPen(QPen(self.selection_color, 2, Qt.PenStyle.DashDotLine))
            painter.drawRect(int(self._x - 5), int(self._y - 5), int(self._width + 10), int(self._height + 10))

    def contains(self, point):
        if not (self._x <= point.x() <= self._x + self._width and self._y <= point.y() <= self._y + self._height):
            return False
        return any(child.contains(point) for child in self._children)

    def move(self, dx, dy, fw, fh):
        new_x = self._x + dx
        new_y = self._y + dy
        if not (0 <= new_x and new_x + self._width <= fw and 0 <= new_y and new_y + self._height <= fh):
            return False
        for child in self._children:
            child.move(dx, dy, fw, fh)
        self._update_bounds()
        return True

    def resize_shape(self, dw, dh, fw, fh):
        if not self._children: return False
        scale_x = 1 + dw / max(self._width, 1)
        scale_y = 1 + dh / max(self._height, 1)
        for child in self._children:
            rel_x = child.x - self._x
            rel_y = child.y - self._y
            new_w = child.width * scale_x
            new_h = child.height * scale_y
            new_x = self._x + rel_x * scale_x
            new_y = self._y + rel_y * scale_y
            if new_x < 0 or new_y < 0 or new_x + new_w > fw or new_y + new_h > fh:
                return False
        for child in self._children:
            rel_x = child.x - self._x
            rel_y = child.y - self._y
            child.width = child.width * scale_x
            child.height = child.height * scale_y
            child.x = self._x + rel_x * scale_x
            child.y = self._y + rel_y * scale_y
        self._update_bounds()
        return True

    def adjust_to_bounds(self, fw, fh):
        for child in self._children:
            child.adjust_to_bounds(fw, fh)
        self._update_bounds()

    def get_bounding_rect(self):
        return (self._x, self._y, self._width, self._height)

    def get_children(self):
        return self._children.copy()

    def get_type_name(self):
        return 'group'

    def set_color(self, color: QColor):
        for child in self._children:
            child.set_color(color)

    def save(self):
        return {
            'id': self.id,
            'type': 'group',
            'x': self._x,
            'y': self._y,
            'width': self._width,
            'height': self._height,
            'is_selected': self.is_selected,
            'children': [c.save() for c in self._children]
        }

    def load(self, data):
        self._id = data.get('id', self._id)
        self._x = data['x']
        self._y = data['y']
        self._width = data['width']
        self._height = data['height']
        self.is_selected = data['is_selected']
        self._children = []
        for child_data in data['children']:
            child = ShapeFactory.create_shape(child_data['type'])
            child.load(child_data)
            self._children.append(child)
        self._update_bounds()


class ShapeFactory:
    @staticmethod
    def create_shape(shape_type: str, x: float = 0, y: float = 0) -> Component:
        if shape_type == 'circle':
            return Circle(x, y)
        elif shape_type == 'rectangle':
            return Rectangle(x, y)
        elif shape_type == 'triangle':
            return Triangle(x, y)
        elif shape_type == 'line':
            return Line(x, y)
        elif shape_type == 'group':
            return Group()
        else:
            raise ValueError(f"Неизвестный тип: {shape_type}")


class FiguresContainer(Subject):
    def __init__(self):
        super().__init__()
        self._shapes: List[Component] = []

    def add(self, shape: Component):
        self._shapes.append(shape)
        self.notify()

    def remove(self, shape: Component):
        if shape in self._shapes:
            to_remove = [shape]
            if not isinstance(shape, Arrow):
                arrows = [s for s in self._shapes if isinstance(s, Arrow) and (s.source == shape or s.target == shape)]
                to_remove.extend(arrows)
            for item in to_remove:
                if item in self._shapes:
                    self._shapes.remove(item)
            self.notify()

    def get_all(self):
        return self._shapes.copy()

    def clear_selected(self):
        for s in [s for s in self._shapes if s.is_selected]:
            self.remove(s)

    def get_selected(self):
        return [s for s in self._shapes if s.is_selected]

    def group_selected(self):
        selected = [s for s in self.get_selected() if not isinstance(s, Arrow)]
        if len(selected) < 2: return None
        group = Group()
        for s in selected:
            self._shapes.remove(s)
            group.add(s)
            s.is_selected = False
        self._shapes.append(group)
        group.is_selected = True
        self.notify()
        return group

    def ungroup_selected(self):
        changed = False
        for shape in list(self._shapes):
            if isinstance(shape, Group) and shape.is_selected:
                children = shape.get_children()
                for fig in self._shapes:
                    if isinstance(fig, Arrow):
                        if fig.source == shape:
                            fig.source = children[0] if children else None
                        if fig.target == shape:
                            fig.target = children[0] if children else None
                self._shapes.remove(shape)
                for child in children:
                    child.is_selected = True
                    self._shapes.append(child)
                changed = True
        if changed:
            self.notify()

    def save_to_file(self, filename: str) -> bool:
        try:
            data = {'version': 1.1, 'shapes': [s.save() for s in self._shapes]}
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(e)
            return False

    def load_from_file(self, filename: str) -> bool:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._shapes.clear()
            loaded_shapes = {}
            arrows_data = []
            for shape_data in data['shapes']:
                if shape_data['type'] == 'arrow':
                    arrows_data.append(shape_data)
                    continue
                shape = ShapeFactory.create_shape(shape_data['type'])
                shape.load(shape_data)
                self._shapes.append(shape)
                self._register_ids(shape, loaded_shapes)
            for arrow_data in arrows_data:
                dummy = Circle(0, 0)
                arrow = Arrow(dummy, dummy)
                arrow.load(arrow_data)
                src = loaded_shapes.get(arrow._saved_source_id)
                tgt = loaded_shapes.get(arrow._saved_target_id)
                if src and tgt:
                    arrow.source = src
                    arrow.target = tgt
                    self._shapes.append(arrow)
            self.notify()
            return True
        except Exception as e:
            print(e)
            return False

    def _register_ids(self, component, registry):
        registry[component.id] = component
        for child in component.get_children():
            self._register_ids(child, registry)


class TreeViewModel(QAbstractItemModel):
    def __init__(self, container: FiguresContainer):
        super().__init__()
        self.container = container
        self.container.changed.connect(self._on_container_changed)
        self.root_item = {"name": "Root", "object": None, "children": []}
        self._build_tree()

    def _on_container_changed(self):
        self.beginResetModel()
        self._build_tree()
        self.endResetModel()

    def _build_tree(self):
        self.root_item["children"].clear()
        shapes = self.container.get_all()
        for i, shape in enumerate(shapes):
            self._add_node(shape, self.root_item, i + 1)

    def _add_node(self, shape, parent_node, index):
        name = f"Объект {index} ({shape.get_type_name()})"
        item = {"name": name, "object": shape, "children": [], "parent": parent_node}
        parent_node["children"].append(item)
        for j, child in enumerate(shape.get_children()):
            self._add_node(child, item, j + 1)

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent): return QModelIndex()
        parent_item = parent.internalPointer() if parent.isValid() else self.root_item
        if row < len(parent_item["children"]):
            return self.createIndex(row, column, parent_item["children"][row])
        return QModelIndex()

    def parent(self, index):
        if not index.isValid(): return QModelIndex()
        child_item = index.internalPointer()
        parent_item = child_item.get("parent")
        if parent_item is None or parent_item is self.root_item:
            return QModelIndex()
        grandparent = parent_item.get("parent")
        if grandparent:
            row = grandparent["children"].index(parent_item)
            return self.createIndex(row, 0, parent_item)
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0: return 0
        parent_item = parent.internalPointer() if parent.isValid() else self.root_item
        return len(parent_item["children"])

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid(): return None
        item = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            return item["name"]
        elif role == Qt.ItemDataRole.CheckStateRole:
            obj = item["object"]
            if obj is not None:
                return Qt.CheckState.Checked if obj.is_selected else Qt.CheckState.Unchecked
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.CheckStateRole and index.isValid():
            item = index.internalPointer()
            obj = item["object"]
            if obj is not None:
                obj.is_selected = (value == Qt.CheckState.Checked.value)
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
                self.container.notify()
                return True
        return False

    def flags(self, index):
        if not index.isValid(): return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable


class Form(QWidget):
    def __init__(self, container: FiguresContainer):
        super().__init__()
        self.container = container
        self.figure_type = None
        self.creating_arrow = False
        self.arrow_source = None
        self.last_mouse_pos = None
        self.dragging = False
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setStyleSheet("background-color: white;")

    def set_figure_type(self, figure_type):
        self.figure_type = figure_type
        self.creating_arrow = (figure_type == 'arrow')
        self.arrow_source = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("white"))  # Белый фон
        for figure in self.container.get_all():
            figure.draw(painter)

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton: return
        pos = event.pos()
        self.last_mouse_pos = pos

        if self.creating_arrow:
            clicked_object = self._find_object_at(pos)
            if clicked_object and not isinstance(clicked_object, Arrow):
                if self.arrow_source is None:
                    self.arrow_source = clicked_object
                    clicked_object.is_selected = True
                else:
                    if clicked_object != self.arrow_source:
                        arrow = Arrow(self.arrow_source, clicked_object)
                        self.container.add(arrow)
                    self.arrow_source.is_selected = False
                    self.arrow_source = None
                self.container.notify()
            return

        clicked_obj = self._find_object_at(pos)
        ctrl_pressed = event.modifiers() & Qt.KeyboardModifier.ControlModifier
        if not ctrl_pressed:
            for shape in self.container.get_all():
                shape.is_selected = False
        if clicked_obj:
            clicked_obj.is_selected = not clicked_obj.is_selected if ctrl_pressed else True
            self.dragging = True
        else:
            if self.figure_type and not self.creating_arrow:
                new_shape = ShapeFactory.create_shape(self.figure_type, pos.x(), pos.y())
                new_shape.is_selected = True
                self.container.add(new_shape)
        self.container.notify()

    def _find_object_at(self, pos):
        for shape in reversed(self.container.get_all()):
            if shape.contains(pos):
                return shape
        return None

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            if self.last_mouse_pos:
                dx = event.pos().x() - self.last_mouse_pos.x()
                dy = event.pos().y() - self.last_mouse_pos.y()
                selected = self.container.get_selected()
                for shape in selected:
                    shape.move(dx, dy, self.width(), self.height())
                self.last_mouse_pos = event.pos()
                self.container.notify()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.container.clear_selected()
        elif event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
            dx, dy = 0, 0
            step = 5
            if event.key() == Qt.Key.Key_Left: dx = -step
            elif event.key() == Qt.Key.Key_Right: dx = step
            elif event.key() == Qt.Key.Key_Up: dy = -step
            elif event.key() == Qt.Key.Key_Down: dy = step
            selected = self.container.get_selected()
            for shape in selected:
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    shape.resize_shape(dx, dy, self.width(), self.height())
                else:
                    shape.move(dx, dy, self.width(), self.height())
            self.container.notify()
        elif event.key() == Qt.Key.Key_G and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.container.group_selected()
        elif event.key() == Qt.Key.Key_U and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.container.ungroup_selected()

    def change_selected_color(self, color):
        for shape in self.container.get_selected():
            shape.set_color(color)
        self.container.notify()


class Okno(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("mainWindow")
        self.resize(1200, 800)
        self.container = FiguresContainer()
        self.form = Form(self.container)
        self.container.changed.connect(self.form.update)

        self.tree_view = QTreeView()
        self.tree_view.setStyleSheet("background-color: white; color: black;")
        self.model = TreeViewModel(self.container)
        self.tree_view.setModel(self.model)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.clicked.connect(self.on_tree_item_clicked)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.tree_view)
        splitter.addWidget(self.form)
        splitter.setSizes([300, 900])
        self.setCentralWidget(splitter)

        self.toolbar()

    def toolbar(self):
        tb = QToolBar()
        self.addToolBar(tb)

        tb.addAction("Круг", lambda: self.form.set_figure_type('circle'))
        tb.addAction("Прямоугольник", lambda: self.form.set_figure_type('rectangle'))
        tb.addAction("Треугольник", lambda: self.form.set_figure_type('triangle'))
        tb.addAction("Линия", lambda: self.form.set_figure_type('line'))
        tb.addAction("Стрелка", lambda: self.form.set_figure_type('arrow'))
        tb.addAction("Группировать", self.container.group_selected)
        tb.addAction("Разгруппировать", self.container.ungroup_selected)
        tb.addAction("Изменить цвет", self.change_color)
        tb.addAction("Сохранить", self.save_project)
        tb.addAction("Загрузить", self.load_project)
#
    def change_color(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.form.change_selected_color(col)

    def save_project(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Сохранить", "", "Text Files (*.txt)")
        if fname:
            self.container.save_to_file(fname)

    def load_project(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Загрузить", "", "Text Files (*.txt)")
        if fname:
            self.container.load_from_file(fname)

    def on_tree_item_clicked(self, index):
        item = index.internalPointer()
        shape = item.get("object")
        if shape:
            ctrl = QApplication.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier
            if not ctrl:
                for s in self.container.get_all():
                    s.is_selected = False
            shape.is_selected = not shape.is_selected
            self.container.notify()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    w = Okno()
    w.show()
    sys.exit(app.exec())