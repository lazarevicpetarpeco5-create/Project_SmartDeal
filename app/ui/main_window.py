import os
import json
import requests
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QTextEdit, QLabel, QPushButton, QMessageBox, QFileDialog,
    QDialog, QFormLayout, QLineEdit
)
from PySide6.QtCore import Qt
from app.services.ai_service import AIService
from app.models.analysis import AnalysisResult


TELECOM_STYLESHEET = """
/* Glavno okno in ozadje */
QMainWindow, QDialog {
    background-color: #F0F4F8;
    color: #1A252C;
    font-family: 'Segoe UI', Arial, sans-serif;
}

/* Oznake (Labels) */
QLabel {
    color: #0A3D62;
    font-size: 13px;
}

/* Vnosna polja za besedilo */
QTextEdit, QLineEdit {
    background-color: #FFFFFF;
    border: 1px solid #B0C4DE;
    border-radius: 6px;
    padding: 8px;
    color: #1A252C;
    font-size: 13px;
    selection-background-color: #38ADA9;
}

QTextEdit:focus, QLineEdit:focus {
    border: 1px solid #1B4F72;
    background-color: #FFFFFF;
}

/* Glavni gumb za AI Analizo */
QPushButton#btn_analyze {
    background-color: #0A3D62;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 13px;
    border: none;
    border-radius: 6px;
    padding: 10px;
}

QPushButton#btn_analyze:hover {
    background-color: #1B4F72;
}

QPushButton#btn_analyze:pressed {
    background-color: #0C2461;
}

/* Sekundarni gumbi (CRM, PDF, Nastavitve) */
QPushButton {
    background-color: #E1E8ED;
    color: #0A3D62;
    font-weight: 600;
    font-size: 12px;
    border: 1px solid #B0C4DE;
    border-radius: 6px;
    padding: 7px 14px;
}

QPushButton:hover {
    background-color: #D4E1ED;
    border-color: #0A3D62;
}

QPushButton:pressed {
    background-color: #B0C4DE;
}
"""


class SettingsDialog(QDialog):
    """Dialog za nastavljanje API ključev in CRM končne točke."""
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Nastavitve sistema")
        self.resize(450, 220)
        self.setStyleSheet(TELECOM_STYLESHEET)

        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.txt_openai_key = QLineEdit(self.config.get("OPENAI_API_KEY", ""))
        self.txt_openai_key.setEchoMode(QLineEdit.Password)
        self.txt_openai_key.setPlaceholderText("Pusti prazno ali 'MOCK' za testni način")

        self.txt_crm_url = QLineEdit(self.config.get("CRM_API_URL", ""))
        self.txt_crm_key = QLineEdit(self.config.get("CRM_API_KEY", ""))
        self.txt_crm_key.setEchoMode(QLineEdit.Password)

        layout.addRow(QLabel("<b>OpenAI API Ključ:</b>"), self.txt_openai_key)
        layout.addRow(QLabel("<b>CRM API URL:</b>"), self.txt_crm_url)
        layout.addRow(QLabel("<b>CRM API Ključ:</b>"), self.txt_crm_key)

        self.btn_save = QPushButton("Shrani nastavitve")
        self.btn_save.clicked.connect(self.save_settings)
        layout.addRow(self.btn_save)

    def save_settings(self):
        self.config["OPENAI_API_KEY"] = self.txt_openai_key.text().strip()
        self.config["CRM_API_URL"] = self.txt_crm_url.text().strip()
        self.config["CRM_API_KEY"] = self.txt_crm_key.text().strip()

        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
            QMessageBox.information(self, "Uspeh", "Nastavitve so bile uspešno shranjene v config.json!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Napaka", f"Shranjevanje nastavitev ni uspelo: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.setWindowTitle("SmartDeal - AI Obdelava Sestankov")
        self.resize(1180, 820)
        self.setStyleSheet(TELECOM_STYLESHEET)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # --- LEVI PANEL: Transkript ---
        left_layout = QVBoxLayout()
        
        top_bar = QHBoxLayout()
        lbl_left_title = QLabel("<b>VNOS TRANSKRIPTA SESTANKA:</b>")
        lbl_left_title.setStyleSheet("font-size: 14px; color: #0A3D62;")
        top_bar.addWidget(lbl_left_title)
        
        self.btn_settings = QPushButton("⚙ Nastavitve (API / CRM)")
        self.btn_settings.clicked.connect(self.open_settings)
        top_bar.addWidget(self.btn_settings)
        left_layout.addLayout(top_bar)

        self.txt_transcript = QTextEdit()
        self.txt_transcript.setPlaceholderText("Prilepite transkript ali uvozite datoteko sestanka...")
        left_layout.addWidget(self.txt_transcript)

        self.btn_analyze = QPushButton("⚡ Analiziraj z AI (gpt-4o-mini)")
        self.btn_analyze.setObjectName("btn_analyze")
        self.btn_analyze.clicked.connect(self.handle_analysis)
        left_layout.addWidget(self.btn_analyze)

        # --- DESNI PANEL: Human-in-the-Loop Urejanje ---
        right_layout = QVBoxLayout()
        lbl_right_title = QLabel("<b>PREGLED IN UREJANJE PODATKOV (Human-in-the-Loop):</b>")
        lbl_right_title.setStyleSheet("font-size: 14px; color: #0A3D62;")
        right_layout.addWidget(lbl_right_title)

        right_layout.addWidget(QLabel("1. Povzetek sestanka:"))
        self.edit_summary = QTextEdit()
        right_layout.addWidget(self.edit_summary)

        right_layout.addWidget(QLabel("2. Zahteve in potrebe stranke:"))
        self.edit_requirements = QTextEdit()
        right_layout.addWidget(self.edit_requirements)

        right_layout.addWidget(QLabel("3. Naslednji koraki in ODGOVORNE OSEBE:"))
        self.edit_action_items = QTextEdit()
        right_layout.addWidget(self.edit_action_items)

        right_layout.addWidget(QLabel("4. Osnutek Follow-up sporočila za stranko:"))
        self.edit_follow_up = QTextEdit()
        right_layout.addWidget(self.edit_follow_up)

        # Gumbi na dnu
        btn_layout = QHBoxLayout()
        self.btn_crm = QPushButton("📤 Pošlji v CRM API")
        self.btn_crm.clicked.connect(self.handle_send_crm)
        
        self.btn_pdf = QPushButton("📄 Izvozi v PDF")
        self.btn_pdf.clicked.connect(self.handle_export_pdf)

        btn_layout.addWidget(self.btn_crm)
        btn_layout.addWidget(self.btn_pdf)
        right_layout.addLayout(btn_layout)

        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(right_layout, stretch=1)

    def open_settings(self):
        dialog = SettingsDialog(self.config, self)
        dialog.exec()

    def handle_analysis(self):
        text = self.txt_transcript.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Opozorilo", "Prosimo, vnesite transkript sestanka.")
            return

        api_key = self.config.get("OPENAI_API_KEY", "")

        try:
            ai_service = AIService(api_key=api_key)
            result: AnalysisResult = ai_service.analyze_transcript(text)

            self.edit_summary.setText(result.summary)
            self.edit_requirements.setText(result.client_requirements)
            self.edit_action_items.setText(result.action_items)
            self.edit_follow_up.setText(result.follow_up_email)

            QMessageBox.information(self, "Uspeh", "Analiza uspešno opravljena! Preglejte in po potrebi uredite izluščene podatke.")
        except Exception as e:
            QMessageBox.critical(self, "Napaka pri obdelavi", f"Prišlo je do napake pri AI analizi:\n{str(e)}")

    def get_current_data(self) -> AnalysisResult:
        return AnalysisResult(
            summary=self.edit_summary.toPlainText(),
            client_requirements=self.edit_requirements.toPlainText(),
            action_items=self.edit_action_items.toPlainText(),
            follow_up_email=self.edit_follow_up.toPlainText()
        )

    def handle_send_crm(self):
        crm_url = self.config.get("CRM_API_URL", "")
        crm_key = self.config.get("CRM_API_KEY", "")

        if not crm_url:
            QMessageBox.warning(self, "Opozorilo", "CRM API URL ni nastavljen. Vnesite ga v nastavitvah.")
            return

        data = self.get_current_data()
        headers = {
            "Authorization": f"Bearer {crm_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(crm_url, json=data.to_dict(), headers=headers, timeout=5)
            if response.status_code in (200, 201):
                QMessageBox.information(self, "CRM Sinhronizacija", "Podatki so bili uspešno poslani v CRM sistem!")
            else:
                QMessageBox.warning(self, "CRM Napaka", f"Strežnik je vrnil status {response.status_code}: {response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Napaka pri povezavi", f"Pošiljanje v CRM ni uspelo:\n{str(e)}")

    def handle_export_pdf(self):
        data = self.get_current_data()
        file_path, _ = QFileDialog.getSaveFileName(self, "Shrani PDF poročilo", "SmartDeal_Porocilo.pdf", "PDF Datoteke (*.pdf)")
        
        if not file_path:
            return

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            c = canvas.Canvas(file_path, pagesize=letter)
            text_object = c.beginText(40, 750)
            text_object.setFont("Helvetica-Bold", 14)
            text_object.textLine("SmartDeal - Poročilo o Sestanku")
            text_object.setFont("Helvetica", 10)
            text_object.textLine("")

            sections = [
                ("POVZETEK SESTANKA:", data.summary),
                ("ZAHTEVE STRANKE:", data.client_requirements),
                ("NASLEDNJI KORAKI IN ODGOVORNI:", data.action_items),
                ("OSNUTEK FOLLOW-UP SPOROČILA:", data.follow_up_email)
            ]

            for title, content in sections:
                text_object.setFont("Helvetica-Bold", 11)
                text_object.textLine(title)
                text_object.setFont("Helvetica", 10)
                for line in content.split("\n"):
                    text_object.textLine(line)
                text_object.textLine("")

            c.drawText(text_object)
            c.save()
            QMessageBox.information(self, "PDF Ustvarjen", f"Poročilo je shranjeno v:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Napaka", f"Generiranje PDF ni uspelo:\n{str(e)}")