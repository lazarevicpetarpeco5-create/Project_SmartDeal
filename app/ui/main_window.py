# app/ui/main_window.py

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SmartDeal")
        self.resize(1200, 800)
        self.showMaximized()

        # Main application container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main background shade (#cbd5e1)
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #cbd5e1;
            }
        """)

        # Main vertical layout
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 25, 40, 25)
        layout.setSpacing(20)

        central_widget.setLayout(layout)

        # Application title
        title = QLabel("SmartDeal")
        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 38px;
            font-weight: bold;
            color: #16a34a;
        """)

        layout.addWidget(title)

        # Transcript input
        self.transcript_input = QTextEdit()
        self.transcript_input.setPlaceholderText(
            "Vstavi pogovor stranke tukaj..."
        )

        self.transcript_input.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #94a3b8;
                border-radius: 8px;
                padding: 12px;
                font-size: 15px;
                color: #0f172a;
            }
        """)

        layout.addWidget(self.transcript_input)

        # Bottom button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        import_button = QPushButton("Import")
        self.analyze_button = QPushButton("Analyze")
        save_button = QPushButton("Save Results")
        history_button = QPushButton("History")

        # Button styling
        button_style = """
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }

            QPushButton:pressed {
                background-color: #1e40af;
            }
        """

        import_button.setStyleSheet(button_style)
        self.analyze_button.setStyleSheet(button_style)
        save_button.setStyleSheet(button_style)
        history_button.setStyleSheet(button_style)

        button_layout.addWidget(import_button)
        button_layout.addWidget(self.analyze_button)
        self.analyze_button.clicked.connect(self.analyze_transcript)
        button_layout.addWidget(save_button)
        button_layout.addWidget(history_button)

        layout.addLayout(button_layout)

    def analyze_transcript(self):
        text = self.transcript_input.toPlainText()
        print(f"Analyzing transcript ({len(text)} characters)...")