import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase
from MAIN import DashboardWindow

def load_fonts():
    """
    Loads all .ttf fonts from the 'fonts' directory and its subdirectories.
    """
    font_dir = "fonts"
    if not os.path.exists(font_dir):
        print(f"Font directory '{font_dir}' not found. Skipping font loading.")
        return

    for root, _, files in os.walk(font_dir):
        for file in files:
            if file.endswith(".ttf"):
                font_path = os.path.join(root, file)





if __name__ == "__main__":
    """
    This is the main entry point for the application.
    
    This script initializes the Qt application, loads custom fonts, and then
    shows the main dashboard window. It is designed to be cross-platform.
    """
    app = QApplication(sys.argv)
    
    # Load custom fonts to ensure cross-platform UI consistency
    load_fonts()
    
    w = DashboardWindow()
    w.show()
    sys.exit(app.exec())
