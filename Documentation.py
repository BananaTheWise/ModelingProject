from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QApplication,
    QTextEdit,
)
from PySide6.QtCore import Qt
import sys

class Documentation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Documentation")
        self.setFixedSize(310, 557)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.center_on_screen()

        # Main widget and layout
        central = QWidget()
        central.setStyleSheet("""
            background-color: #4C4C4C;
            border-radius: 25px;
        """)
        self.setCentralWidget(central)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Read-only text area with scroll
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)  # Make it non-editable
        self.text_area.setStyleSheet("""
            QTextEdit {
                background-color: #CDCDCD;
                border-radius: 8px;
                padding: 8px;
                font.size : 12;
                color: #333333;
            }
        """)
        # Set some sample text (replace with your actual documentation)
        self.text_area.setText("""
1) Problem Formulation: We have traffic on a 4-way conjunction road, traffic happens during peak hours, regular traffic lights may not adapt well to real time traffic variations leading to a long queue and unhappy citizens.
        
2) Goals and objectives: primary goal of this simulation is to improve traffic control at a 4 way conjunction road and we aim to:
- represent the real-world traffic
- Asses how different traffic light cycles affect the traffic
- provide a decision support system for engineers to test on.
our objectives are:
How do random vehicle arrivals affect traffic
how does fixed time cycle affect the arrival rate
what is the throughput under different traffic loads
when does system breakdown and what are the conditions for it.

3) Model conceptualization: System is a 4-way intersection consisting of North, South, East, West. Our entities are vehicle arrivals.
events consist of vehicle arrival, vehicle departure, traffic light change.
we will judge our model by average delay, queue length and the throughput of the cars.
We will assume that the drivers are sane people and follow the rules, no outside events like accidents and vehicle arrivals are random but are realistic.

4) Data collection: we will collect data about traffic demand data like arrival rates.
fixed time cycle of traffic light.
Type of cars, Queue lengths. PS: we will get data from Kaggle.

5) Model translation: Simulation model will run for 3 weeks of simulation times and will evaluate the performance of the model based on:
Traffic light change: how much time does it take the traffic light to change from green to red.
Average waiting time: how much time did each car wait
queue length: how many cars are in the queue.
Throughput: how many cars passed by a single green traffic light.

6) Verification and validation: 
We will verify the model by checking if it’s a true representation of our road and will run according to peak times of traffic, we will then observe the flow with the government through animated runs to verify it is working.
Validation: we will compare the output results with the output of real system by loading in previous data of current road if there is >=85% similarity then the model is verified.

7) We will run the simulation for 3 weeks for time-of-day from 12 pm to 7pm. We will run this simulation 3 times and analyze the output of each run. If the performance turns out as we expected then we will document the model and simulation and submit it for future maintenance, then we will implement the model in real life. Else, if the performance doesn’t improve then we will simulate it more than 3 times and if that doesn’t work, we will change the simulation duration to different periods and different time period.
        """)
        layout.addWidget(self.text_area)

        # Back button (red, like in SecondAssignment)
        self.back_btn = QPushButton("Back")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                padding: 8px;
            }
        """)
        self.back_btn.clicked.connect(self.BackToMain)
        layout.addWidget(self.back_btn)

        central.setLayout(layout)

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
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def BackToMain(self):
        from MAIN import DashboardWindow
        self.main = DashboardWindow()
        self.main.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Documentation()
    w.show()
    sys.exit(app.exec())
