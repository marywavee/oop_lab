import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QSlider
)
from PyQt6.QtCore import Qt


class Model:
    MIN_VALUE = 0
    MAX_VALUE = 100

    def __init__(self):
        self.A = 10
        self.B = 50
        self.C = 90


class MainWindow(QMainWindow):
    def __init__(self, model: Model):
        super().__init__()
        self.model = model
        self.setWindowTitle("mainWindow")
        self.resize(600, 300)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(20)
        root.setContentsMargins(40, 30, 40, 30)

        # === Заголовок: A <= B <= C ===
        header = QHBoxLayout()
        header.setSpacing(20)

        self.lblA = QLabel("A")
        self.lblA.setStyleSheet("font-size: 32px; font-weight: bold; color: black;")
        self.lblA.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lblLE1 = QLabel("<=")
        self.lblLE1.setStyleSheet("font-size: 32px; color: black;")
        self.lblLE1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lblB = QLabel("B")
        self.lblB.setStyleSheet("font-size: 32px; font-weight: bold; color: black;")
        self.lblB.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lblLE2 = QLabel("<=")
        self.lblLE2.setStyleSheet("font-size: 32px; color: black;")
        self.lblLE2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lblC = QLabel("C")
        self.lblC.setStyleSheet("font-size: 32px; font-weight: bold; color: black;")
        self.lblC.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header.addWidget(self.lblA)
        header.addWidget(self.lblLE1)
        header.addWidget(self.lblB)
        header.addWidget(self.lblLE2)
        header.addWidget(self.lblC)
        root.addLayout(header)

        # === Три колонки с контролами ===
        controls = QHBoxLayout()
        controls.setSpacing(40)

        # --- Колонка A ---
        colA = QVBoxLayout()
        colA.setSpacing(10)
        self.a_text = QLineEdit("10")
        self.a_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.a_text.setStyleSheet("font-size: 16px; color: black; background-color: white; border: 1px solid gray;")
        self.a_spin = QSpinBox()
        self.a_spin.setRange(0, 100)
        self.a_spin.setValue(10)
        self.a_spin.setStyleSheet("color: black;")
        self.a_slider = QSlider(Qt.Orientation.Horizontal)
        self.a_slider.setRange(0, 100)
        self.a_slider.setValue(10)

        colA.addWidget(self.a_text)
        colA.addWidget(self.a_spin)
        colA.addWidget(self.a_slider)
        controls.addLayout(colA)

        # --- Колонка B ---
        colB = QVBoxLayout()
        colB.setSpacing(10)
        self.b_text = QLineEdit("50")
        self.b_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.b_text.setStyleSheet("font-size: 16px; color: black; background-color: white; border: 1px solid gray;")
        self.b_spin = QSpinBox()
        self.b_spin.setRange(0, 100)
        self.b_spin.setValue(50)
        self.b_spin.setStyleSheet("color: black;")
        self.b_slider = QSlider(Qt.Orientation.Horizontal)
        self.b_slider.setRange(0, 100)
        self.b_slider.setValue(50)

        colB.addWidget(self.b_text)
        colB.addWidget(self.b_spin)
        colB.addWidget(self.b_slider)
        controls.addLayout(colB)

        # --- Колонка C ---
        colC = QVBoxLayout()
        colC.setSpacing(10)
        self.c_text = QLineEdit("90")
        self.c_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.c_text.setStyleSheet("font-size: 16px; color: black; background-color: white; border: 1px solid gray;")
        self.c_spin = QSpinBox()
        self.c_spin.setRange(0, 100)
        self.c_spin.setValue(90)
        self.c_spin.setStyleSheet("color: black;")
        self.c_slider = QSlider(Qt.Orientation.Horizontal)
        self.c_slider.setRange(0, 100)
        self.c_slider.setValue(90)

        colC.addWidget(self.c_text)
        colC.addWidget(self.c_spin)
        colC.addWidget(self.c_slider)
        controls.addLayout(colC)

        root.addLayout(controls)
        central.setStyleSheet("background-color: white;")

        # === СИНХРОНИЗАЦИЯ ===
        self.setup_sync(self.a_text, self.a_spin, self.a_slider)
        self.setup_sync(self.b_text, self.b_spin, self.b_slider)
        self.setup_sync(self.c_text, self.c_spin, self.c_slider)

    def setup_sync(self, text: QLineEdit, spin: QSpinBox, slider: QSlider):
        def on_text_changed(input_str):
            if not input_str:
                return
            try:
                value = int(input_str)
                if 0 <= value <= 100:
                    self.update_all(text, spin, slider, value)
            except ValueError:
                pass

        def on_spin_changed(value):
            self.update_all(text, spin, slider, value)

        def on_slider_changed(value):
            self.update_all(text, spin, slider, value)

        text.textChanged.connect(on_text_changed)
        spin.valueChanged.connect(on_spin_changed)
        slider.valueChanged.connect(on_slider_changed)

    def update_all(self, text: QLineEdit, spin: QSpinBox, slider: QSlider, value: int):
        text.blockSignals(True)
        spin.blockSignals(True)
        slider.blockSignals(True)

        text.setText(str(value))
        spin.setValue(value)
        slider.setValue(value)

        text.blockSignals(False)
        spin.blockSignals(False)
        slider.blockSignals(False)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    model = Model()
    window = MainWindow(model)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()