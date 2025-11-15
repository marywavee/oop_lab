import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QSlider
)
from PyQt6.QtCore import Qt

class Model:
    class Model:
        MIN_VALUE = 0
        MAX_VALUE = 100

        def __init__(self):
            self.A = 0
            self.B = 0
            self.C = 0

class MainWindow(QMainWindow):
    def __init__(self, model: Model):
        super().__init__()

        self.model = model

        self.setWindowTitle("mainWindow")
        self.resize(900, 350)

        central = QWidget()
        root = QVBoxLayout(central)

        titles = QHBoxLayout()

        self.lblA = QLabel("A")
        self.lblA.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblA.setStyleSheet("font-size: 32px; font-weight: bold;")

        self.lblLE1 = QLabel("<=")
        self.lblLE1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblLE1.setStyleSheet("font-size: 32px;")

        self.lblB = QLabel("B")
        self.lblB.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblB.setStyleSheet("font-size: 32px; font-weight: bold;")

        self.lblLE2 = QLabel("<=")
        self.lblLE2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblLE2.setStyleSheet("font-size: 32px;")

        self.lblC = QLabel("C")
        self.lblC.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblC.setStyleSheet("font-size: 32px; font-weight: bold;")

        titles.addWidget(self.lblA)
        titles.addWidget(self.lblLE1)
        titles.addWidget(self.lblB)
        titles.addWidget(self.lblLE2)
        titles.addWidget(self.lblC)

        root.addLayout(titles)

        row_widgets = QHBoxLayout()

        #Колонка A
        colA = QVBoxLayout()
        self.a_text = QLineEdit()     #
        self.a_spin = QSpinBox()
        self.a_spin.setRange(0, 100)
        self.a_slider = QSlider(Qt.Orientation.Horizontal)
        self.a_slider.setRange(0, 100)

        colA.addWidget(self.a_text)
        colA.addWidget(self.a_spin)
        colA.addWidget(self.a_slider)

        #Колонка B
        colB = QVBoxLayout()
        self.b_text = QLineEdit()
        self.b_spin = QSpinBox()
        self.b_spin.setRange(0, 100)
        self.b_slider = QSlider(Qt.Orientation.Horizontal)
        self.b_slider.setRange(0, 100)

        colB.addWidget(self.b_text)
        colB.addWidget(self.b_spin)
        colB.addWidget(self.b_slider)

        #Колонка C
        colC = QVBoxLayout()
        self.c_text = QLineEdit()
        self.c_spin = QSpinBox()
        self.c_spin.setRange(0, 100)
        self.c_slider = QSlider(Qt.Orientation.Horizontal)
        self.c_slider.setRange(0, 100)

        colC.addWidget(self.c_text)
        colC.addWidget(self.c_spin)
        colC.addWidget(self.c_slider)

        # Добавляем 3 колонки
        row_widgets.addLayout(colA)
        row_widgets.addLayout(colB)
        row_widgets.addLayout(colC)

        root.addLayout(row_widgets)

        self.setCentralWidget(central)
        self.setStyleSheet("background-color: white;")



def main():
    app = QApplication(sys.argv)

    model = Model()
    window = MainWindow(model)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
