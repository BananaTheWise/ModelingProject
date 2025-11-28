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

        self.nav_layout = QHBoxLayout()
        self.nav_layout.setContentsMargins(0, 0, 0, 0)

    def add_nav_buttons(self, prev_callback=None, next_callback=None, prev_text="Back", next_text="Next"):
        self.prev_btn = QPushButton(prev_text)
        self.next_btn = QPushButton(next_text)
        self.prev_btn.setFixedSize(100,30)
        self.next_btn.setFixedSize(100,30)
        self.prev_btn.setStyleSheet("""
            background-color: #C23731; color: #1E1E1E; border: 2px solid black; border-radius: 15px;
        """)
        self.next_btn.setStyleSheet("""
            background-color: #61AF5E; color: #1E1E1E; border: 2px solid black; border-radius: 15px;
        """)
        if prev_callback: self.prev_btn.clicked.connect(prev_callback)
        if next_callback: self.next_btn.clicked.connect(next_callback)
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

    def create_title(self, text, width=180):
        title_btn = QPushButton(text)
        title_btn.setEnabled(False)
        title_btn.setFixedSize(width, 30)
        title_btn.setStyleSheet("""
            background-color: #CDCDCD; border: 2px solid #BBBBBB; border-radius: 12px;
            font-size: 17px; color: #2C2C2C;
        """)
        return title_btn

    def _create_input_row(self, layout, label_text, example_text, default_value, width=60, height=20):
        row = QHBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("color: white; font-size: 14px;")
        field = self.make_field("", width=width, height=height)
        field.setText(default_value)
        
        example_label = QLabel(example_text)
        example_label.setStyleSheet("color: gray; font-size: 12px;")

        row.addWidget(label)
        row.addStretch()
        row.addWidget(field)
        layout.addLayout(row)
        
        if example_text:
            example_row = QHBoxLayout()
            example_row.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            example_row.addWidget(example_label)
            layout.addLayout(example_row)
            
        return field
