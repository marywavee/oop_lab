import sys
from PySide6    .QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
import math
from typing import List, Optional

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab 3")
        self.resize(800, 600)

from PySide6.QtCore import QPoint

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
