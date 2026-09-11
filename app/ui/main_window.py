from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SmartDeal")
        self.resize(1200, 800)
        self.showMaximized()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        title = QLabel("SmartDeal")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: blue;
        """)

        layout.addWidget(title)

        transcript_input = QTextEdit()
        transcript_input.setPlaceholderText(
            "Vstavi pogovor stranke tukaj..."
        )
        transcript_input.setMaximumHeight(400)

        layout.addWidget(transcript_input)

        button_layout = QHBoxLayout()

        import_button = QPushButton("Import")
        analyze_button = QPushButton("Analyze")
        save_button = QPushButton("Save Results")
        history_button = QPushButton("History")

        button_layout.addWidget(import_button)
        button_layout.addWidget(analyze_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(history_button)

        layout.addLayout(button_layout)