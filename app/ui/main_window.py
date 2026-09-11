from PySide6.QtWidgets import QMainWindow, QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SmartDeal")
        self.resize(1200, 800)
        self.showMaximized()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)