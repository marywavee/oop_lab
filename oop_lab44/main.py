# main.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QToolBar, QColorDialog
)
from PyQt6.QtGui import QAction, QActionGroup, QColor
from PyQt6.QtCore import Qt

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.current_color = QColor("#0066ff")
        self.current_tool = "pointer"

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#f8f8f8"))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("mainWindow")
        self.resize(1000, 700)

        central = QWidget()
        layout = QVBoxLayout(central)
        self.canvas = Canvas()
        layout.addWidget(self.canvas)
        self.setCentralWidget(central)

        self.create_toolbar()

    def create_toolbar(self):
        tb = QToolBar("Инструменты")
        self.addToolBar(tb)

        group = QActionGroup(self)
        group.setExclusive(True)

        tools = ["pointer", "circle", "rectangle", "triangle", "line"]
        names = ["Указатель", "Круг", "Прямоугольник", "Треугольник", "Отрезок"]

        for tool, name in zip(tools, names):
            act = QAction(name, self)
            act.setCheckable(True)
            if tool == "pointer":
                act.setChecked(True)
            act.triggered.connect(lambda checked, t=tool: setattr(self.canvas, "current_tool", t))
            group.addAction(act)
            tb.addAction(act)

        tb.addSeparator()
        color_act = QAction("Цвет", self)
        color_act.triggered.connect(self.choose_color)
        tb.addAction(color_act)

    def choose_color(self):
        color = QColorDialog.getColor(self.canvas.current_color)
        if color.isValid():
            self.canvas.current_color = color

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec()