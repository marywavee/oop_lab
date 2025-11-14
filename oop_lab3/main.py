import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout
)
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QPainter, QPen, QBrush

class CCircle:
    def __init__(self, center: QPoint, radius: int = 20):
        self._center = QPoint(center)
        self._radius = radius
        self._selected = False

    def draw(self, painter: QPainter):
        pen = QPen(Qt.red if self._selected else Qt.blue, 2)
        brush = QBrush(Qt.white)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawEllipse(self._center, self._radius, self._radius)

    def contains(self, p: QPoint):
        dx = p.x() - self._center.x()
        dy = p.y() - self._center.y()
        return dx * dx + dy * dy <= self._radius * self._radius

    def center(self):
        return QPoint(self._center)

    def radius(self):
        return self._radius

    def isSelected(self):
        return self._selected

    def setSelected(self, state: bool):
        self._selected = state

class Storage:
    def __init__(self):
        self._items = []

    def addCircle(self, c: CCircle):
        self._items.append(c)

    def getCircle(self, i: int) -> CCircle:
        return self._items[i]

    def getCount(self) -> int:
        return len(self._items)

    def removeCircle(self, i: int):
        if 0 <= i < len(self._items):
            del self._items[i]

    def __iter__(self):
        return iter(self._items)

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.storage = Storage()
        self.setFocusPolicy(Qt.StrongFocus)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for c in self.storage:
            c.draw(painter)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()


            self.storage.addCircle(CCircle(pos))

            self.update()
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab 3")
        self.resize(800, 600)

        central = QWidget()
        layout = QVBoxLayout(central)
        self.canvas = Canvas()
        layout.addWidget(self.canvas)
        self.setCentralWidget(central)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())