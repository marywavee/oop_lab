import sys
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject


# === МОДЕЛЬ ===
class Model(QObject):
    data_changed = pyqtSignal()
    MIN_VALUE = 0
    MAX_VALUE = 100
    SAVE_FILE = "values.json"

    def __init__(self):
        super().__init__()
        self.A = 10
        self.B = 50
        self.C = 90
        self._load()

    def _emit_if_changed(self, old_a, old_b, old_c):
        if (old_a != self.A or old_b != self.B or old_c != self.C):
            self.data_changed.emit()

    def set_A(self, value: int):
        value = max(self.MIN_VALUE, min(self.MAX_VALUE, value))
        old_a, old_b, old_c = self.A, self.B, self.C

        self.A = value
        if self.A > self.B:
            self.B = self.A
        if self.A > self.C:
            self.C = self.A
            self.B = self.A

        self._emit_if_changed(old_a, old_b, old_c)

    def set_B(self, value: int):
        value = max(self.MIN_VALUE, min(self.MAX_VALUE, value))
        old_a, old_b, old_c = self.A, self.B, self.C

        self.B = max(self.A, min(self.C, value))

        self._emit_if_changed(old_a, old_b, old_c)

    def set_C(self, value: int):
        value = max(self.MIN_VALUE, min(self.MAX_VALUE, value))
        old_a, old_b, old_c = self.A, self.B, self.C

        self.C = value
        if self.C < self.B:
            self.B = self.C
        if self.C < self.A:
            self.A = self.C
            self.B = self.C

        self._emit_if_changed(old_a, old_b, old_c)

    def save(self):
        data = {"A": self.A, "B": self.B, "C": self.C}
        try:
            with open(self.SAVE_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Save failed: {e}")

    def _load(self):
        if not os.path.exists(self.SAVE_FILE):
            return
        try:
            with open(self.SAVE_FILE, "r") as f:
                data = json.load(f)
                if all(k in data for k in ("A", "B", "C")):
                    a = max(self.MIN_VALUE, min(self.MAX_VALUE, data["A"]))
                    c = max(self.MIN_VALUE, min(self.MAX_VALUE, data["C"]))
                    b = max(self.MIN_VALUE, min(self.MAX_VALUE, data["B"]))
                    self.A, self.B, self.C = a, b, c
                    self.set_A(a)
        except Exception as e:
            print(f"Load failed: {e}")


# === ПРЕДСТАВЛЕНИЕ ===
class MainWindow(QMainWindow):
    def __init__(self, model: Model):
        super().__init__()
        self.model = model
        self.setWindowTitle("mainWindow")
        self.resize(600, 340)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(20)
        root.setContentsMargins(40, 30, 40, 30)

        # === Заголовок ===
        header = QHBoxLayout()
        header.setSpacing(20)
        for text in ["A", "<=", "B", "<=", "C"]:
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            style = "font-size: 32px; color: black;"
            if text in ("A", "B", "C"):
                style += " font-weight: bold;"
            lbl.setStyleSheet(style)
            header.addWidget(lbl)
        root.addLayout(header)

        # === Контролы ===
        controls = QHBoxLayout()
        controls.setSpacing(40)

        def make_column():
            col = QVBoxLayout()
            col.setSpacing(10)
            text = QLineEdit()
            text.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text.setStyleSheet("font-size: 16px; color: black; background-color: white; border: 1px solid gray;")
            spin = QSpinBox()
            spin.setRange(0, 100)
            spin.setStyleSheet("color: black;")
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 100)
            col.addWidget(text)
            col.addWidget(spin)
            col.addWidget(slider)
            return text, spin, slider, col

        self.a_text, self.a_spin, self.a_slider, colA = make_column()
        self.b_text, self.b_spin, self.b_slider, colB = make_column()
        self.c_text, self.c_spin, self.c_slider, colC = make_column()

        controls.addLayout(colA)
        controls.addLayout(colB)
        controls.addLayout(colC)
        root.addLayout(controls)

        # === СЧЁТЧИК ОБНОВЛЕНИЙ ===
        self.update_label = QLabel("UI updates: 0")
        self.update_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_label.setStyleSheet("font-size: 14px; color: gray;")
        root.addWidget(self.update_label)

        self.update_count = 0

        central.setStyleSheet("background-color: white;")

        # === Инициализация ===
        self.update_ui()
        self.update_count += 1
        self.update_label.setText(f"UI updates: {self.update_count}")

        # === Подписка ===
        self.model.data_changed.connect(self.on_model_changed)

        self.a_text.textChanged.connect(lambda t: self.try_set(self.model.set_A, t))
        self.a_spin.valueChanged.connect(lambda v: self.model.set_A(v))
        self.a_slider.valueChanged.connect(lambda v: self.model.set_A(v))

        self.b_text.textChanged.connect(lambda t: self.try_set(self.model.set_B, t))
        self.b_spin.valueChanged.connect(lambda v: self.model.set_B(v))
        self.b_slider.valueChanged.connect(lambda v: self.model.set_B(v))

        self.c_text.textChanged.connect(lambda t: self.try_set(self.model.set_C, t))
        self.c_spin.valueChanged.connect(lambda v: self.model.set_C(v))
        self.c_slider.valueChanged.connect(lambda v: self.model.set_C(v))

    def try_set(self, setter, text):
        if not text.strip():
            return
        try:
            value = int(text)
            setter(value)
        except ValueError:
            pass

    def on_model_changed(self):
        self.update_count += 1
        self.update_label.setText(f"UI updates: {self.update_count}")
        self.update_ui()

    def update_ui(self):
        a, b, c = self.model.A, self.model.B, self.model.C

        for text, spin, slider, val in [
            (self.a_text, self.a_spin, self.a_slider, a),
            (self.b_text, self.b_spin, self.b_slider, b),
            (self.c_text, self.c_spin, self.c_slider, c)
        ]:
            text.blockSignals(True)
            spin.blockSignals(True)
            slider.blockSignals(True)
            text.setText(str(val))
            spin.setValue(val)
            slider.setValue(val)
            text.blockSignals(False)
            spin.blockSignals(False)
            slider.blockSignals(False)

    def closeEvent(self, event):
        self.model.save()
        super().closeEvent(event)



def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    model = Model()
    window = MainWindow(model)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()