import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
import math
from typing import List, Optional


#Базовый абстрактный класс для графических объектов.
class GraphicObject:
    def contains(self, point: QPoint) -> bool:

        raise NotImplementedError()

    def draw(self, painter: QPainter):

        raise NotImplementedError()

    def is_selected(self) -> bool:

        raise NotImplementedError()

    def set_selected(self, selected: bool):

        raise NotImplementedError()
