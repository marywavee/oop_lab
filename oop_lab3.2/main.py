import sys
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QKeyEvent


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
        if old_a != self.A or old_b != self.B or old_c != self.C:
            self.data_changed.emit()

    def set_A(self, value: int):
        value = max(self.MIN_VALUE, min(self.MAX_VALUE, value))
        old_a, old_b, old_c = self.A, self.B, self.C

        if value > self.C:
            value = self.C

        self.A = value

        if self.A > self.B:
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

        if value < self.A:
            value = self.A

        self.C = value

        if self.C < self.B:
            self.B = self.C

        self._emit_if_changed(old_a, old_b, old_c)

    def save(self):
        data = {"A": self.A, "C": self.C}
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
                if "A" in data and "C" in data:
                    a = max(self.MIN_VALUE, min(self.MAX_VALUE, data["A"]))
                    c = max(self.MIN_VALUE, min(self.MAX_VALUE, data["C"]))

                    if a <= c:
                        self.A = a
                        self.C = c
                    else:
                        self.A = c
                        self.C = a

                    self.B = (self.A + self.C) // 2
        except Exception as e:
            print(f"Load failed: {e}")


class EnterLineEdit(QLineEdit):
    enter_pressed = pyqtSignal()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.enter_pressed.emit()
        super().keyPressEvent(event)


class EnterSpinBox(QSpinBox):
    enter_pressed = pyqtSignal()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.enter_pressed.emit()
        super().keyPressEvent(event)


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

        controls = QHBoxLayout()
        controls.setSpacing(40)

        def make_column():
            col = QVBoxLayout()
            col.setSpacing(10)
            text = EnterLineEdit()
            text.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text.setStyleSheet("font-size: 16px; color: black; background-color: white; border: 1px solid gray;")
            spin = EnterSpinBox()
            spin.setRange(0, 100)
            spin.setStyleSheet("color: black;")
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 100)          # Шкала всегда 0–100
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

        self.update_label = QLabel("UI updates: 0")
        self.update_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_label.setStyleSheet("font-size: 14px; color: gray;")
        root.addWidget(self.update_label)
        self.update_count = 0

        central.setStyleSheet("background-color: white;")

        self.update_ui()
        self.update_count = 1
        self.update_label.setText(f"UI updates: {self.update_count}")

        self.model.data_changed.connect(self.on_model_changed)

        # Текстовые поля и спинбоксы — только по Enter
        self.a_text.enter_pressed.connect(lambda: self.try_set_from_text(self.model.set_A, self.a_text.text()))
        self.b_text.enter_pressed.connect(lambda: self.try_set_from_text(self.model.set_B, self.b_text.text()))
        self.c_text.enter_pressed.connect(lambda: self.try_set_from_text(self.model.set_C, self.c_text.text()))

        self.a_spin.enter_pressed.connect(lambda: self.try_set_from_spin(self.model.set_A, self.a_spin.value()))
        self.b_spin.enter_pressed.connect(lambda: self.try_set_from_spin(self.model.set_B, self.b_spin.value()))
        self.c_spin.enter_pressed.connect(lambda: self.try_set_from_spin(self.model.set_C, self.c_spin.value()))

        # СЛАЙДЕРЫ: теперь не дают выйти за границы, но шкала 0–100
        self.a_slider.sliderMoved.connect(self.limit_slider_a)
        self.a_slider.valueChanged.connect(self.model.set_A)

        self.b_slider.sliderMoved.connect(self.limit_slider_b)
        self.b_slider.valueChanged.connect(self.model.set_B)

        self.c_slider.sliderMoved.connect(self.limit_slider_c)
        self.c_slider.valueChanged.connect(self.model.set_C)

    # Ограничители для слайдеров (шкала 0–100, но ползунок "упирается")
    def limit_slider_a(self, pos):
        if pos > self.model.C:
            self.a_slider.setValue(self.model.C)

    def limit_slider_b(self, pos):
        if pos < self.model.A:
            self.b_slider.setValue(self.model.A)
        elif pos > self.model.C:
            self.b_slider.setValue(self.model.C)

    def limit_slider_c(self, pos):
        if pos < self.model.A:
            self.c_slider.setValue(self.model.A)

    def try_set_from_text(self, setter, text):
        if not text.strip():
            return
        try:
            value = int(text)
            old_val = value
            setter(value)
            self.model.save()
            # Если B обрезался — форсируем обновление UI
            if setter == self.model.set_B and self.model.B != old_val:
                self.model.data_changed.emit()
        except ValueError:
            pass

    def try_set_from_spin(self, setter, value):
        setter(value)
        self.model.save()

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
    #asdasdad