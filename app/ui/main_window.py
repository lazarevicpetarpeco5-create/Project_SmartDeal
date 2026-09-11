import json
import os
import platform
import subprocess
from datetime import datetime

import requests
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.models.analysis import AnalysisResult
from app.services.ai_service import AIService

CONFIG_FILE = "config.json"


def load_config():
    """Naloži nastavitve iz config.json ali vrne privzete."""
    default_config = {
        "crm_api_url": "https://httpbin.org/post",
        "crm_api_key": "demo_key",
        "openai_api_key": "",
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                default_config.update(config)
        except Exception:
            pass
    return default_config


def save_config(config_data):
    """Shrani nastavitve v config.json."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


class SettingsDialog(QDialog):
    """Dialog okno za nastavljanje API ključev in CRM vmesnika."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nastavitve API in CRM Povezave")
        self.setFixedSize(450, 250)

        config = load_config()

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.crm_url_input = QLineEdit(config.get("crm_api_url", ""))
        self.crm_key_input = QLineEdit(config.get("crm_api_key", ""))
        self.openai_key_input = QLineEdit(config.get("openai_api_key", ""))
        self.openai_key_input.setEchoMode(QLineEdit.Password)

        form_layout.addRow(QLabel("CRM API URL:"), self.crm_url_input)
        form_layout.addRow(QLabel("CRM API Ključ:"), self.crm_key_input)
        form_layout.addRow(
            QLabel("OpenAI API Ključ:"), self.openai_key_input
        )

        layout.addLayout(form_layout)

        # Gumbi za shranjevanje / preklic
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Shrani")
        cancel_btn = QPushButton("Preklic")

        save_btn.setStyleSheet(
            "background-color: #16a34a; color: white; font-weight: bold; padding:"
            " 6px 12px; border-radius: 4px;"
        )
        cancel_btn.setStyleSheet(
            "background-color: #64748b; color: white; padding: 6px 12px;"
            " border-radius: 4px;"
        )

        save_btn.clicked.connect(self.save)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def save(self):
        new_config = {
            "crm_api_url": self.crm_url_input.text().strip(),
            "crm_api_key": self.crm_key_input.text().strip(),
            "openai_api_key": self.openai_key_input.text().strip(),
        }
        save_config(new_config)

        # Če je vpisan OpenAI ključ, ga nastavimo tudi v okolju
        if new_config["openai_api_key"]:
            os.environ["OPENAI_API_KEY"] = new_config["openai_api_key"]

        QMessageBox.information(
            self, "Uspeh", "Nastavitve so bile uspešno shranjene!"
        )
        self.accept()


class AnalysisThread(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, transcript: str):
        super().__init__()
        self.transcript = transcript

    def run(self):
        try:
            config = load_config()
            api_key = config.get("openai_api_key") or os.getenv(
                "OPENAI_API_KEY"
            )
            service = AIService(api_key=api_key)
            result = service.analyze(self.transcript)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartDeal - Human-in-the-Loop AI Asistent")
        self.resize(1200, 800)
        self.showMaximized()

        self.last_generated_pdf = None

        # Nastavitev privzete OpenAI tipke iz konfiguracije (če obstaja)
        config = load_config()
        if config.get("openai_api_key"):
            os.environ["OPENAI_API_KEY"] = config["openai_api_key"]

        self.default_pdf_dir = os.path.join(
            os.path.expanduser("~"), "Dokumenti"
        )
        if not os.path.exists(self.default_pdf_dir):
            self.default_pdf_dir = os.path.expanduser("~")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet(
            "QWidget { background-color: #cbd5e1; }"
        )

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)

        # --- ZGORNJA VRSTICA: Naslov + Nastavitve + Mapa za PDF ---
        top_header_layout = QHBoxLayout()

        title = QLabel("SmartDeal: AI Validacija Transkriptov & CRM Gateway")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #16a34a;"
        )

        # Gumb za nastavitve
        settings_btn = QPushButton("⚙ Nastavitve API/CRM")
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #0f172a;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1e293b; }
        """)

        # Nadzorna plošča za pot shranjevanja PDF
        folder_container = QWidget()
        folder_layout = QHBoxLayout(folder_container)
        folder_layout.setContentsMargins(0, 0, 0, 0)
        folder_layout.setSpacing(8)

        folder_label = QLabel("Mapa za PDF:")
        folder_label.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #334155;"
        )

        self.folder_path_input = QLineEdit(self.default_pdf_dir)
        self.folder_path_input.setReadOnly(True)
        self.folder_path_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #94a3b8;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 12px;
                color: #0f172a;
                min-width: 180px;
            }
        """)

        change_folder_btn = QPushButton("Spremeni...")
        change_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #475569;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #334155; }
        """)

        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_path_input)
        folder_layout.addWidget(change_folder_btn)

        top_header_layout.addWidget(title)
        top_header_layout.addStretch()
        top_header_layout.addWidget(settings_btn)
        top_header_layout.addWidget(folder_container)

        main_layout.addLayout(top_header_layout)

        # --- OSREDNJI DEL: Splitter ---
        splitter = QSplitter(Qt.Horizontal)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        left_label = QLabel("Vhodni Transkript Sestanka:")
        left_label.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #1e293b;"
        )
        self.transcript_input = QTextEdit()
        self.transcript_input.setPlaceholderText(
            "Vlepite transkript pogovora ali uvozite .txt/.md datoteko..."
        )
        self.transcript_input.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff; border: 1px solid #94a3b8;
                border-radius: 8px; padding: 12px; font-size: 14px; color: #0f172a;
            }
        """)
        left_layout.addWidget(left_label)
        left_layout.addWidget(self.transcript_input)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        right_label = QLabel("Strukturirani Podatki (Pregled & Validacija):")
        right_label.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #1e293b;"
        )
        self.result_output = QTextEdit()
        self.result_output.setPlaceholderText(
            "Rezultat analize se bo prikazal tukaj. Pred pošiljanjem v CRM lahko"
            " podatke ročno urejate..."
        )
        self.result_output.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff; border: 1px solid #94a3b8;
                border-radius: 8px; padding: 12px; font-size: 14px; color: #0f172a;
            }
        """)
        right_layout.addWidget(right_label)
        right_layout.addWidget(self.result_output)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 700])
        main_layout.addWidget(splitter)

        # --- SPODNJI GUMBI ---
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        import_btn = QPushButton("Uvozi Datoteko")
        self.analyze_btn = QPushButton("Analiziraj z AI")
        export_pdf_btn = QPushButton("Izvozi v PDF")
        self.open_file_btn = QPushButton("Odpri PDF")
        sync_crm_btn = QPushButton("Potrdi in Pošlji v CRM")

        button_style = """
            QPushButton {
                background-color: #2563eb; color: white; border: none;
                border-radius: 6px; padding: 10px 14px; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """
        action_style = """
            QPushButton {
                background-color: #0284c7; color: white; border: none;
                border-radius: 6px; padding: 10px 14px; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background-color: #0369a1; }
        """
        sync_style = """
            QPushButton {
                background-color: #16a34a; color: white; border: none;
                border-radius: 6px; padding: 10px 14px; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background-color: #15803d; }
        """

        import_btn.setStyleSheet(button_style)
        self.analyze_btn.setStyleSheet(button_style)
        export_pdf_btn.setStyleSheet(action_style)
        self.open_file_btn.setStyleSheet(action_style)
        sync_crm_btn.setStyleSheet(sync_style)

        button_layout.addWidget(import_btn)
        button_layout.addWidget(self.analyze_btn)
        button_layout.addWidget(export_pdf_btn)
        button_layout.addWidget(self.open_file_btn)
        button_layout.addWidget(sync_crm_btn)

        main_layout.addLayout(button_layout)

        # Povezave akcij
        settings_btn.clicked.connect(self.open_settings)
        change_folder_btn.clicked.connect(self.select_storage_folder)
        import_btn.clicked.connect(self.import_file)
        self.analyze_btn.clicked.connect(self.analyze_transcript)
        export_pdf_btn.clicked.connect(self.export_to_pdf)
        self.open_file_btn.clicked.connect(self.open_pdf)
        sync_crm_btn.clicked.connect(self.sync_to_crm)

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def select_storage_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Izberi mapo za shranjevanje PDF poročil", self.default_pdf_dir
        )
        if folder:
            self.default_pdf_dir = folder
            self.folder_path_input.setText(folder)

    def import_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Odpri transkript", "", "Besedilne datoteke (*.txt *.md)"
        )
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.transcript_input.setText(f.read())

    def analyze_transcript(self):
        text = self.transcript_input.toPlainText()
        if not text.strip():
            QMessageBox.warning(
                self, "Opozorilo", "Vnesite ali uvozite besedilo za analizo."
            )
            return

        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("Analiziram...")

        self.thread = AnalysisThread(text)
        self.thread.finished.connect(self.on_analysis_success)
        self.thread.error.connect(self.on_analysis_error)
        self.thread.start()

    def on_analysis_success(self, result: AnalysisResult):
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("Analiziraj z AI")

        needs_formatted = "\n".join(
            [f"- {need}" for need in result.customer_needs]
        )
        formatted_text = (
            f"POVZETEK:\n{result.summary}\n\n"
            f"ODNOS STRANKE:\n{result.customer_sentiment}\n\n"
            f"GLAVNA TEŽAVA:\n{result.main_issue}\n\n"
            f"POTREBE STRANKE:\n{needs_formatted}\n\n"
            f"PRIPOROČEN UKREP:\n{result.recommended_action}"
        )
        self.result_output.setText(formatted_text)

    def on_analysis_error(self, err_msg: str):
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("Analiziraj z AI")
        QMessageBox.critical(
            self, "Napaka", f"Prišlo je do napake pri analizi: {err_msg}"
        )

    def export_to_pdf(self):
        content = self.result_output.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Opozorilo", "Ni vsebine za izvoz v PDF.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SmartDeal_Porocilo_{timestamp}.pdf"
        full_path = os.path.join(self.default_pdf_dir, filename)

        try:
            config = load_config()
            service = AIService(api_key=config.get("openai_api_key"))
            service.generate_pdf(content, full_path)
            self.last_generated_pdf = full_path
            QMessageBox.information(
                self,
                "Uspeh",
                f"PDF dokument je bil uspešno ustvarjen in shranjen v:\n{full_path}",
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Napaka", f"Napaka pri ustvarjanju PDF: {e}"
            )

    def open_pdf(self):
        if (
            not self.last_generated_pdf
            or not os.path.exists(self.last_generated_pdf)
        ):
            QMessageBox.warning(
                self,
                "Opozorilo",
                "Najprej izvozite PDF datoteko ali preverite izbrano mapo.",
            )
            return

        if platform.system() == "Linux":
            subprocess.run(["xdg-open", self.last_generated_pdf])
        elif platform.system() == "Windows":
            os.startfile(self.last_generated_pdf)
        elif platform.system() == "Darwin":
            subprocess.run(["open", self.last_generated_pdf])

    def sync_to_crm(self):
        content = self.result_output.toPlainText().strip()
        if not content:
            QMessageBox.warning(
                self, "Opozorilo", "Ni preverjenih podatkov za pošiljanje."
            )
            return

        config = load_config()
        crm_url = config.get("crm_api_url")
        crm_key = config.get("crm_api_key")

        headers = {
            "Authorization": f"Bearer {crm_key}",
            "Content-Type": "application/json",
        }
        payload = {"data": content, "source": "SmartDeal Desktop App"}

        try:
            response = requests.post(
                crm_url, json=payload, headers=headers, timeout=5
            )
            if response.status_code in [200, 201]:
                QMessageBox.information(
                    self,
                    "Uspeh",
                    f"Podatki so bili uspešno poslani na CRM:\n{crm_url}",
                )
            else:
                QMessageBox.critical(
                    self,
                    "Napaka CRM",
                    f"CRM strežnik je vrnil status kodo: {response.status_code}",
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Napaka Povezave", f"Ne morem se povezati s CRM: {e}"
            )