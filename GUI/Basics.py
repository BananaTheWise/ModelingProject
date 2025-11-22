from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QHBoxLayout,
    QCheckBox,
    QStackedWidget,
    QRadioButton,
    QSpacerItem,
    QSizePolicy, QButtonGroup, QMessageBox, QApplication,
)
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QMessageBox
import random
from PySide6.QtCore import Qt
from MAIN import DashboardWindow

class BasePage(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(12)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setAlignment(Qt.AlignTop)

        # Navigation layout at bottom
        self.nav_layout = QHBoxLayout()
        self.nav_layout.setContentsMargins(0, 0, 0, 0)

    def add_nav_buttons(self, prev_callback=None, next_callback=None, prev_text="Back", next_text="Next"):

        self.prev_btn = QPushButton(prev_text)
        self.next_btn = QPushButton(next_text)
        self.prev_btn.setFixedSize(100,30)
        self.next_btn.setFixedSize(100,30)
        self.prev_btn.setStyleSheet("""
            background-color: #C23731;
            color: #1E1E1E;
            border: 2px solid black;
            border-radius: 15px;  /* bigger = more rounded */
        """)

        self.next_btn.setStyleSheet("""
            background-color: #61AF5E;
            color: #1E1E1E;
            border: 2px solid black;
            border-radius: 15px;  /* bigger = more rounded */
        """)

        if prev_callback:
            self.prev_btn.clicked.connect(prev_callback)
        if next_callback:
            self.next_btn.clicked.connect(next_callback)

        # Add buttons to nav layout with stretch between
        self.nav_layout.addWidget(self.prev_btn, alignment=Qt.AlignLeft)
        self.nav_layout.addStretch()
        self.nav_layout.addWidget(self.next_btn, alignment=Qt.AlignRight)

    def centered_row(self, widget):
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(widget)
        row.addStretch()
        return row

    def make_field(self, placeholder, width=60, height=20):
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setFixedSize(width, height)
        field.setStyleSheet("color: black; background: #fff; border-radius: 8px;")
        return field
