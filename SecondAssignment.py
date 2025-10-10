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
    QSizePolicy, QButtonGroup,
)
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

    def add_nav_buttons(self, prev_callback=None, next_callback=None):

        self.prev_btn = QPushButton("Back")
        self.next_btn = QPushButton("Next")
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
        field.setStyleSheet("background: #fff; border-radius: 8px;")
        return field

###########################################################################

class SecondAssignment(QMainWindow):

    def go_prev(self):
        idx = self.stacked.currentIndex()
        if idx > 0:
            self.stacked.setCurrentIndex(idx - 1)

    def go_next(self):
        idx = self.stacked.currentIndex()

        # If not last page → go next normally
        if idx < self.stacked.count() - 1:
            self.stacked.setCurrentIndex(idx + 1)
        else:
            # On the last page (Page4)
            page4 = self.pages[-1]  # get last page object
            selected = page4.selected_option()

            if not selected:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "No Option Selected", "Please choose an output option first.")
                return

            # Example: handle different selections
            if "Excel" in selected:
                print("Exporting results to Excel...")
                # call your Excel export function here
            elif "GUI" in selected:
                print("Displaying results in GUI...")
                # show another window
            elif "Terminal" in selected:
                print("Printing results to terminal...")
                # print output or save file

            # Optionally close the window after action
            self.close()

    def mousePressEvent(self, event):
        self._drag_pos = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def __init__(self, num_pages=3):
        super().__init__()
        self.setWindowTitle("Second Assignment")
        self.setFixedSize(310, 557)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        central = QWidget()
        central.setStyleSheet("""
            background-color: #4C4C4C;
            border-radius: 25px;
        """)
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.stacked = QStackedWidget()
        self.pages = [
            Page1(prev_callback=self.handle_back, next_callback=self.go_next),
            Page2(prev_callback=self.go_prev, next_callback=self.go_next),
            Page3(prev_callback=self.go_prev, next_callback=self.go_next),
            Page4(prev_callback=self.go_prev, next_callback=self.go_next)
        ]

        for page in self.pages:
            self.stacked.addWidget(page)

        main_layout.addWidget(self.stacked)

        central.setLayout(main_layout)

    def handle_back(self):
        # If on first page, close window (return to main)
        if self.stacked.currentIndex() == 0:
            self.dashboard = DashboardWindow()
            self.dashboard.show()
            self.close()
        else:
            self.go_prev()

###########################################################################

class Page1(BasePage):
    def __init__(self, prev_callback=None, next_callback=None):
        super().__init__()

        # --- Title ---
        title_btn = QPushButton("Interarrival Time")
        title_btn.setEnabled(False)
        title_btn.setFixedSize(167, 30)
        title_btn.setStyleSheet("""
               background-color: #CDCDCD;
               border: 2px solid #BBBBBB;
               border-radius: 12px;
               font-size: 17px;
               color: #2C2C2C;
           """)
        self.main_layout.addLayout(self.centered_row(title_btn))

        # Fake space under title
        self.main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- Range section ---
        range_label = QLabel("Range")
        range_label.setStyleSheet("color: white; font-size: 14px;")

        start_field = self.make_field("Start")
        end_field = self.make_field("End")

        range_row = QHBoxLayout()
        range_row.addWidget(range_label)
        range_row.addStretch()
        range_row.addWidget(start_field)
        range_row.addWidget(end_field)
        self.main_layout.addLayout(range_row)

        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- Equal section ---
        equal_checkbox = QCheckBox("Equal")
        equal_checkbox.setStyleSheet("color: white;")
        equal_text = QLabel("All probabilities are the same")
        equal_text.setStyleSheet("color: gray; font-size: 12px;")
        equal_text.setWordWrap(True)
        self.main_layout.addWidget(equal_checkbox)
        self.main_layout.addWidget(equal_text)
        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- Probabilities section ---
        prob_label = QLabel("Probabilities")
        prob_label.setStyleSheet("color: white; font-size: 14px;")
        prob_field = self.make_field("Sum of Probs. must equal 1", width=200, height=40)
        self.main_layout.addWidget(prob_label)
        self.main_layout.addWidget(prob_field)

        # Push everything up
        self.main_layout.addStretch()

        # --- Nav buttons at bottom ---
        self.main_layout.addLayout(self.nav_layout)
        self.add_nav_buttons(prev_callback, next_callback)

###########################################################################

class Page2(BasePage):
    def __init__(self, prev_callback=None, next_callback=None):
        super().__init__()

        # --- Title ---
        title_btn = QPushButton("Service-Time")
        title_btn.setEnabled(False)
        title_btn.setFixedSize(167, 30)
        title_btn.setStyleSheet("""
               background-color: #CDCDCD;
               border: 2px solid #BBBBBB;
               border-radius: 12px;
               font-size: 17px;
               color: #2C2C2C;
           """)
        self.main_layout.addLayout(self.centered_row(title_btn))

        # Fake space under title
        self.main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- Range section ---
        range_label = QLabel("Range")
        range_label.setStyleSheet("color: white; font-size: 14px;")

        start_field = self.make_field("Start")
        end_field = self.make_field("End")

        range_row = QHBoxLayout()
        range_row.addWidget(range_label)
        range_row.addStretch()
        range_row.addWidget(start_field)
        range_row.addWidget(end_field)
        self.main_layout.addLayout(range_row)

        # Fake space under range
        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- Equal section ---
        equal_checkbox = QCheckBox("Equal")
        equal_checkbox.setStyleSheet("color: white;")
        equal_text = QLabel("All probabilities are the same")
        equal_text.setStyleSheet("color: gray; font-size: 12px;")
        equal_text.setWordWrap(True)
        self.main_layout.addWidget(equal_checkbox)
        self.main_layout.addWidget(equal_text)

        # Fake space under equal section
        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- Probabilities section ---
        prob_label = QLabel("Probabilities")
        prob_label.setStyleSheet("color: white; font-size: 14px;")
        prob_field = self.make_field("Sum of Probs. must equal 1", width=200, height=40)
        self.main_layout.addWidget(prob_label)
        self.main_layout.addWidget(prob_field)

        # Bottom stretch
        self.main_layout.addStretch()

        # --- Nav buttons at bottom ---
        self.main_layout.addLayout(self.nav_layout)
        self.add_nav_buttons(prev_callback, next_callback)

###########################################################################

class Page3(BasePage):
    def __init__(self, prev_callback=None, next_callback=None):
        super().__init__()

        # --- Title ---
        title_btn = QPushButton("Simulation Table")
        title_btn.setEnabled(False)
        title_btn.setFixedSize(167, 30)
        title_btn.setStyleSheet("""
               background-color: #CDCDCD;
               border: 2px solid #BBBBBB;
               border-radius: 12px;
               font-size: 17px;
               color: #2C2C2C;
           """)
        self.main_layout.addLayout(self.centered_row(title_btn))

        # Fake space under title
        self.main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- Range section ---
        range_label = QLabel("How Many Instances")
        range_label.setStyleSheet("color: white; font-size: 14px;")

        start_field = self.make_field("Ex. 20")

        range_row = QHBoxLayout()
        range_row.addWidget(range_label)
        range_row.addStretch()
        range_row.addWidget(start_field)
        self.main_layout.addLayout(range_row)

        # Fake space under range
        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- Radio section ---
        radio_layout = QHBoxLayout()
        traffic_radio = QRadioButton("Traffic")
        traffic_radio.setChecked(True)
        traffic_radio.setStyleSheet("color: white;")
        radio_layout.addWidget(traffic_radio)
        radio_layout.addStretch()
        self.main_layout.addLayout(radio_layout)

        # Bottom stretch
        self.main_layout.addStretch()

        # --- Nav buttons at bottom ---
        self.main_layout.addLayout(self.nav_layout)
        self.add_nav_buttons(prev_callback, next_callback)

###########################################################################

class Page4(BasePage):
    def __init__(self, prev_callback=None, next_callback=None):
        super().__init__()

        # --- Title ---
        title_btn = QPushButton("Output")
        title_btn.setEnabled(False)
        title_btn.setFixedSize(167, 30)
        title_btn.setStyleSheet("""
            background-color: #CDCDCD;
            border: 2px solid #BBBBBB;
            border-radius: 12px;
            font-size: 17px;
            color: #2C2C2C;
        """)
        self.main_layout.addLayout(self.centered_row(title_btn))

        self.main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- Radio Buttons with Read-only Descriptions ---
        options = [
            ("📊 Excel", "Export results to an Excel (.xlsx) file"),
            ("🖥️ Python GUI", "Display results inside the app interface"),
            ("💻 Terminal", "Print results in the console output")
        ]

        self.button_group = QButtonGroup(self)  # store it in self
        self.button_group.setExclusive(True)

        for label_text, description in options:
            radio = QRadioButton(label_text)
            radio.setStyleSheet("color: white; font-size: 14px;")
            self.button_group.addButton(radio)
            self.main_layout.addWidget(radio)

            # --- Description field (read-only QLineEdit) ---
            desc_field = QLineEdit(description)
            desc_field.setReadOnly(True)
            desc_field.setFixedSize(300, 25)
            desc_field.setStyleSheet("""
                background-color: #3A3A3A;
                color: #E0E0E0;
                border: none;
                border-radius: 6px;
                padding-left: 6px;
                font-size: 13px;
            """)
            self.main_layout.addWidget(desc_field, alignment=Qt.AlignCenter)
            self.main_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Bottom stretch
        self.main_layout.addStretch()

        # --- Nav buttons at bottom ---
        self.main_layout.addLayout(self.nav_layout)
        self.add_nav_buttons(prev_callback, next_callback)


    def selected_option(self):
        """Return the text of the selected radio button, or None."""
        selected = self.button_group.checkedButton()
        return selected.text() if selected else None

    @staticmethod
    def generate_interarrival_distribution(start, end, probabilities=None):
        """
        Generate a 2D list for interarrival time distribution.

        Columns:
        [Interarrival Time, Probability, Cumulative Probability, Random-Digit Assignment]

        Random-digit assignment:
          starts at 001 and wraps so the final range ends at 000.
        """

        times = list(range(start, end + 1))
        n = len(times)

        # If equal probabilities selected
        if probabilities is None:
            probabilities = [1 / n] * n

        # Safety check
        if abs(sum(probabilities) - 1) > 1e-6:
            raise ValueError("Sum of probabilities must equal 1.")

        # Compute cumulative probabilities
        cumulative = []
        total = 0
        for p in probabilities:
            total += p
            cumulative.append(round(total, 3))

        # Assign random-digit ranges (001–000)
        random_ranges = []
        current_start = 1  # start from 001

        for i, p in enumerate(probabilities):
            span = round(p * 1000)
            if i == n - 1:
                # Last range ends at 000
                random_ranges.append(f"{current_start:03d} - 000")
            else:
                end_range = current_start + span - 1
                random_ranges.append(f"{current_start:03d} - {end_range:03d}")
                current_start = end_range + 1
                if current_start > 1000:
                    current_start -= 1000

        # Combine into 2D list
        table = []
        for i in range(n):
            row = [
                times[i],
                round(probabilities[i], 3),
                cumulative[i],
                random_ranges[i],
            ]
            table.append(row)

        return table

    @staticmethod
    def generate_service_time_distribution(start, end, probabilities=None):
        """
        Generate a 2D list for service-time distribution.

        Columns:
        [Service Time, Probability, Cumulative Probability, Random-Digit Assignment]

        Random-digit assignment:
          starts at 01 and wraps so the final range ends at 00 (1–100 scale).
        """

        times = list(range(start, end + 1))
        n = len(times)

        # If equal probabilities are not provided
        if probabilities is None:
            probabilities = [1 / n] * n

        # Validate
        if abs(sum(probabilities) - 1) > 1e-6:
            raise ValueError("Sum of probabilities must equal 1.")

        # Compute cumulative probabilities
        cumulative = []
        total = 0
        for p in probabilities:
            total += p
            cumulative.append(round(total, 3))

        # Assign random-digit ranges (01–00)
        random_ranges = []
        current_start = 1  # start from 01

        for i, p in enumerate(probabilities):
            span = round(p * 100)  # because 100 total digits
            if span == 0:
                span = 1  # ensure at least 1 digit

            if i == n - 1:
                random_ranges.append(f"{current_start:02d} - 00")
            else:
                end_range = current_start + span - 1
                random_ranges.append(f"{current_start:02d} - {end_range:02d}")
                current_start = end_range + 1
                if current_start > 100:
                    current_start -= 100

        # Combine into 2D table
        table = []
        for i in range(n):
            row = [
                times[i],
                round(probabilities[i], 3),
                cumulative[i],
                random_ranges[i],
            ]
            table.append(row)

        return table

    @staticmethod
    def assign_interarrival_times(distribution_table, num_users=10):
        """
        Generate a 2D list showing:
        [User, Random Digit, Interarrival Time]

        distribution_table: 2D list from generate_interarrival_distribution
        num_users: how many users to simulate
        """

        # --- Parse ranges from distribution_table ---
        parsed_ranges = []
        for time, prob, cum_prob, r_range in distribution_table:
            start_str, end_str = r_range.replace(' ', '').split('-')
            start = int(start_str)
            end = 1000 if end_str == '000' else int(end_str)
            parsed_ranges.append((time, start, end))

        # --- Generate random digits and assign times ---
        table = []
        for user_id in range(1, num_users + 1):
            random_digit = random.randint(1, 1000)

            # Find which interval this random digit belongs to
            interarrival_time = None
            for time, start, end in parsed_ranges:
                if start <= random_digit <= end or (end == 1000 and random_digit == 1000):
                    interarrival_time = time
                    break
                # wrap case (001–000)
                if start > end and (random_digit >= start or random_digit <= end):
                    interarrival_time = time
                    break

            table.append([user_id, f"{random_digit:03d}", interarrival_time])

        return table

    @staticmethod
    def assign_service_times(distribution_table, num_customers=10):
        """
        Generate a 2D list:
        [Customer, Random Digit, Service Time]

        distribution_table: from generate_service_distribution
        num_customers: number of customers to simulate
        """

        parsed_ranges = []
        for time, prob, cum_prob, r_range in distribution_table:
            start_str, end_str = r_range.replace(' ', '').split('-')
            start = int(start_str)
            end = 100 if end_str == '00' else int(end_str)
            parsed_ranges.append((time, start, end))

        # --- Generate random digits and assign service times ---
        table = []
        for cust_id in range(1, num_customers + 1):
            random_digit = random.randint(1, 100)

            service_time = None
            for time, start, end in parsed_ranges:
                if start <= random_digit <= end or (end == 100 and random_digit == 100):
                    service_time = time
                    break
                # wrap around case like 84–00
                if start > end and (random_digit >= start or random_digit <= end):
                    service_time = time
                    break

            table.append([cust_id, f"{random_digit:02d}", service_time])

        return table

    # --- Step 2: Full Queue Simulation ---
    @staticmethod
    def simulate_queue(interarrival_dist, service_dist, num_users):
        inter_table = Page4.assign_interarrival_times(interarrival_dist, num_users)
        service_table = Page4.assign_service_times(service_dist, num_users)

        simulation = []
        server_available_time = 0

        for i in range(num_users):
            user = i + 1
            interarrival_time = inter_table[i][1]
            service_time = service_table[i][1]

            # Arrival time = previous arrival + interarrival
            if i == 0:
                arrival_time = interarrival_time
            else:
                arrival_time = simulation[i - 1][2] + interarrival_time

            # Service begins when server is free or when user arrives, whichever is later
            service_begin = max(arrival_time, server_available_time)

            # Waiting time in queue
            waiting_time = service_begin - arrival_time

            # Service ends
            service_end = service_begin + service_time

            # Time in system
            time_in_system = waiting_time + service_time

            # Idle time of server
            idle_time = max(0, arrival_time - server_available_time)

            # Update server available time
            server_available_time = service_end

            simulation.append([
                user,
                interarrival_time,
                arrival_time,
                service_time,
                service_begin,
                waiting_time,
                service_end,
                time_in_system,
                idle_time
            ])

        return simulation
