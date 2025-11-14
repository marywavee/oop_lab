import sys
from PySide6    .QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QMessageBox)
from PySide6.QtCore import QPoint
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
import math
from typing import List, Optional

class CCircle:
    def __init__(self, center: QPoint, radius: int = 20):
        self._center = QPoint(center)
        self._radius = radius
        self._selected = False

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
    """Пустой виджет для рисования, пока ничего не делает."""
    def __init__(self):
        super().__init__()
        self.storage = Storage()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # пока не рисуем ничего
        painter.end()
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab 3")
        self.resize(800, 600)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
