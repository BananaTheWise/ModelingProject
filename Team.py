from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QApplication
from PySide6.QtCore import Qt
import sys

class TeamWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Team")
        self.setFixedSize(310, 557)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        central = QWidget()
        central.setStyleSheet("background-color: #4C4C4C; border-radius: 25px;")
        self.setCentralWidget(central)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)


        title_btn = QPushButton("Team Members")
        title_btn.setEnabled(False)
        title_btn.setFixedSize(167, 30)
        title_btn.setStyleSheet(
            """
            background-color: #CDCDCD;
            border: 2px solid #BBBBBB;
            border-radius: 12px;
            font-size: 17px;
            color: #2C2C2C;
            """
        )
        layout.addWidget(title_btn, alignment=Qt.AlignCenter)

        members = [
            "Ahmed Badr 20235622",
            "Hamza Sayed 20232888",
            "Mohamed Sherif 20233901",
            "Nour Eldin Hossam 20232773",
            "Youssef Ahmed 20230172"
        ]
        for name in members:
            lbl = QLabel(name)
            lbl.setStyleSheet("color: white; font-weight: bold; font-size: 15px;")
            lbl.setAlignment(Qt.AlignLeft)
            layout.addWidget(lbl)

        self.back_btn = QPushButton("Back")
        self.back_btn.setStyleSheet("background-color: #d9534f; color: white; font-weight: bold; border-radius: 10px; padding: 8px;")
        self.back_btn.clicked.connect(self.BackToMain)  # ✅ fixed here
        layout.addWidget(self.back_btn)

        central.setLayout(layout)

    def BackToMain(self):
        from MAIN import DashboardWindow
        self.main = DashboardWindow()
        self.main.show()
        self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TeamWindow()
    w.show()
    sys.exit(app.exec())
