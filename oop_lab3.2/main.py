import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

class Model:
    def __init__(self):
        pass

class MainWindow(QMainWindow):
    def __init__(self, model: Model):
        super().__init__()

        self.setStyleSheet("background-color: white;")
        self.model = model
        self.setWindowTitle("mainWindow")
        self.resize(500, 300)



def main():
    app = QApplication(sys.argv)

    model = Model()
    window = MainWindow(model)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
