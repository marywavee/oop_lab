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
    data_changed = pyqtSignal()  # Одно уведомление
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
                    # Применяем с валидацией
                    self.A, self.B, self.C = a, b, c
                    self.set_A(a)  # Чтобы правила сработали
        except Exception as e:
            print(f"Load failed: {e}")


# === ПРЕДСТАВЛЕНИЕ ===
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

        # === Заголовок A <= B <= C ===
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

        central.setStyleSheet("background-color: white;")

        # === Инициализация UI ===
        self.update_ui()

        # === Подписка на модель ===
        self.model.data_changed.connect(self.update_ui)

        # === Подписка на контролы ===
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

    def update_ui(self):
        a, b, c = self.model.A, self.model.B, self.model.C

        # --- A ---
        self.a_text.blockSignals(True)
        self.a_spin.blockSignals(True)
        self.a_slider.blockSignals(True)
        self.a_text.setText(str(a))
        self.a_spin.setValue(a)
        self.a_slider.setValue(a)
        self.a_text.blockSignals(False)
        self.a_spin.blockSignals(False)
        self.a_slider.blockSignals(False)

        # --- B ---
        self.b_text.blockSignals(True)
        self.b_spin.blockSignals(True)
        self.b_slider.blockSignals(True)
        self.b_text.setText(str(b))
        self.b_spin.setValue(b)
        self.b_slider.setValue(b)
        self.b_text.blockSignals(False)
        self.b_spin.blockSignals(False)
        self.b_slider.blockSignals(False)

        # --- C ---
        self.c_text.blockSignals(True)
        self.c_spin.blockSignals(True)
        self.c_slider.blockSignals(True)
        self.c_text.setText(str(c))
        self.c_spin.setValue(c)
        self.c_slider.setValue(c)
        self.c_text.blockSignals(False)
        self.c_spin.blockSignals(False)
        self.c_slider.blockSignals(False)

    def closeEvent(self, event):
        self.model.save()
        super().closeEvent(event)


# === ЗАПУСК ===
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    model = Model()
    window = MainWindow(model)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()