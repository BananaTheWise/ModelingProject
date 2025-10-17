
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QApplication,
)
from PySide6.QtCore import Qt
import sys



class DashboardWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard")
        self.setFixedSize(310, 557)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.center_on_screen()

        central = QWidget()
        central.setStyleSheet("""
            background-color: #838383;
            border-radius: 25px;
        """)
        self.setCentralWidget(central)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        btn_width = 167
        btn_height = 30

        title_btn = QPushButton("0IQMachine")
        title_btn.setEnabled(False)
        title_btn.setFixedSize(btn_width, btn_height)
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

        names = [
            "Documentation",
            "Assignment 2",
            "Assignment 3",
            "Assignment 4",
            "Assignment 5",
            "Team",
        ]

        for n in names:
            b = QPushButton(n)
            b.setFixedHeight(40)
            b.setStyleSheet(
                """
                font-family: Inter, Helvetica, Segoe UI, Arial;
                background-color: #2C2C2C;
                border: 1px solid #2C2C2C;
                border-radius: 10px;
                color: #F5F5F5;
                """
            )
            b.setFixedSize(btn_width, btn_height)
            if n == "Assignment 2":
                b.clicked.connect(self.open_second_assignment)
            elif n == "Assignment 3":
                b.clicked.connect(self.open_third_assignment)
            elif n == "Documentation":
                b.clicked.connect(self.open_Documentation)
            elif n == "Team":
                b.clicked.connect(self.open_Team)
            else:
                b.clicked.connect(self._placeholder_handler)
            layout.addWidget(b, alignment=Qt.AlignCenter)

        exit_btn = QPushButton("Exit")
        exit_btn.setFixedHeight(40)
        exit_btn.setStyleSheet(
            """
            background-color: #C23731;
            color: #1E1E1E;
            font-weight: bold;
            border: 1px solid black;
            border-radius: 10px;
            """
        )
        exit_btn.clicked.connect(self.close)
        exit_btn.setFixedSize(btn_width, btn_height)
        layout.addWidget(exit_btn, alignment=Qt.AlignCenter)

        central.setLayout(layout)

    def _placeholder_handler(self):
        print("Button pressed (not implemented)")

    def open_second_assignment(self):
        from SecondAssignment import SecondAssignment
        self.second_window = SecondAssignment()
        self.second_window.show()
        self.close()

    def open_third_assignment(self):
        from ThirdAssignment import ThirdAssignment
        self.third_window = ThirdAssignment()
        self.third_window.show()
        self.close()

    def open_Documentation(self):
        from Documentation import Documentation
        self.Documentation = Documentation()
        self.Documentation.show()
        self.close()

    def open_Team(self):
        from Team import TeamWindow
        self.Team = TeamWindow()
        self.Team.show()
        self.close()

    def center_on_screen(self):
        # Get screen geometry
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        # Get window geometry
        window_geometry = self.frameGeometry()
        # Calculate center
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def mousePressEvent(self, event):
        self._drag_pos = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = DashboardWindow()
    w.show()
    sys.exit(app.exec())
