import sys
import os
import json
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow

def load_config():
    config_path = "config.json"
    default_config = {
        "OPENAI_API_KEY": "",
        "CRM_API_URL": "https://api.example.com/crm/deals",
        "CRM_API_KEY": ""
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_config
    return default_config

def main():
    app = QApplication(sys.argv)
    config = load_config()
    
    window = MainWindow(config)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()