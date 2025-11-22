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
from GUI.Basics import BasePage
from ALGORITHMS.Second import *
from ALGORITHMS.Third import *

###########################################################################
class Page0(BasePage):
        def __init__(self, prev_callback=None, next_callback=None, defaults=None):
            super().__init__()
            self.prev_callback = prev_callback
            self.next_callback = next_callback

            # --- Title ---
            title_btn = QPushButton("Simulation Setup")
            title_btn.setEnabled(False)
            title_btn.setFixedSize(200, 30)
            title_btn.setStyleSheet("""
                background-color: #CDCDCD;
                border: 2px solid #BBBBBB;
                border-radius: 12px;
                font-size: 17px;
                color: #2C2C2C;
            """)
            self.main_layout.addLayout(self.centered_row(title_btn))

            # Spacer
            self.main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

            # Label + input
            label = QLabel("Enter Number of Servers :")
            label.setStyleSheet("color: white; font-size: 14px;")
            self.num_field = QLineEdit()
            self.num_field.setPlaceholderText("Ex. 2")
            self.num_field.setFixedWidth(200)
            self.num_field.setValidator(QIntValidator(1, 1000))  # ensure integer
            self.num_field.setStyleSheet("background: #ffffff; color: #000000; border-radius: 8px; padding: 6px;")

            self.main_layout.addLayout(self.centered_row(label))
            self.main_layout.addLayout(self.centered_row(self.num_field))

            # push content up
            self.main_layout.addStretch()

            # Nav buttons: pass callbacks to add_nav_buttons
            self.main_layout.addLayout(self.nav_layout)
            # Use local wrapper for next to validate before calling parent's callback
            self.add_nav_buttons(prev_callback=self.prev_callback, next_callback=self._on_next_click)

        def _on_next_click(self):
            text = self.num_field.text().strip()
            if not text:
                QMessageBox.warning(self, "Invalid Input", "Please enter the number of servers.")
                return
            try:
                n = int(text)
                if n <= 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter a positive integer.")
                return

            # call parent's next callback with the parsed integer
            if callable(self.next_callback):
                self.next_callback(n)

        # --- When user clicks Next ---
        def handle_next(self):
            text = self.input.text().strip()
            if not text.isdigit() or int(text) <= 0:
                QMessageBox.warning(self, "Invalid Input", "Please enter a positive integer for number of servers.")
                return
            num_servers = int(text)
            if self.next_callback:
                self.next_callback(num_servers)



class ThirdAssignment(QMainWindow):
    def handle_page0_next(self, num_servers):
        """
        Called when user clicks Next on Page0.
        Dynamically creates the rest of the pages based on num_servers.
        Also initializes default values for all later pages.
        This version is defensive and will show any exception to help debugging.
        """
        try:
            # Validate input
            if not isinstance(num_servers, int) or num_servers <= 0:
                QMessageBox.warning(self, "Invalid Input", "Number of servers must be a positive integer.")
                return

            # Save Page0 input
            self.input_data.setdefault("page0", {})["num_servers"] = num_servers

            # Clear existing pages (except Page0)
            # iterate backwards to avoid index shift
            for i in range(self.stacked.count() - 1, 0, -1):
                widget = self.stacked.widget(i)
                self.stacked.removeWidget(widget)
                try:
                    widget.deleteLater()
                except Exception:
                    pass

            # Reset pages list (keep page0 reference)
            self.pages = [self.page0]

            # --- PAGE 1: Interarrival ---
            page1_defaults = self.input_data.get("page1", {
                "start": 1,
                "end": 5,
                "equal": True,
                # Page1 expects a string in prob_field; keep that shape
                "probabilities": "0.2 0.2 0.2 0.2 0.2"
            })
            page1 = Page1(prev_callback=self.handle_back,
                          next_callback=self.go_next,
                          defaults=page1_defaults)
            self.stacked.addWidget(page1)
            self.pages.append(page1)

            # --- PAGE 2: Service-Time pages (one per server) ---
            # initialize page2_list with defaults for each server
            self.input_data["page2_list"] = []
            for i in range(num_servers):
                defaults = {
                    "start": 1,
                    "end": 5,
                    "equal": True,
                    "probabilities": "0.2 0.2 0.2 0.2 0.2",
                    # optional: keep server identifier so you can show it in the page if desired
                    "server_name": f"Server {i + 1}"
                }
                self.input_data["page2_list"].append(defaults)
                page2 = Page2(prev_callback=self.go_prev,
                              next_callback=self.go_next,
                              defaults=defaults)
                self.stacked.addWidget(page2)
                self.pages.append(page2)

            # --- PAGE 3: Simulation Settings ---
            page3_defaults = self.input_data.get("page3", {
                "instances": 20,
                "traffic_selected": True
            })
            page3 = Page3(prev_callback=self.go_prev,
                          next_callback=self.go_next,
                          defaults=page3_defaults)
            self.stacked.addWidget(page3)
            self.pages.append(page3)

            # --- PAGE 4: Output Selection ---
            page4_defaults = self.input_data.get("page4", {"output_option": None})
            page4 = Page4(prev_callback=self.go_prev,
                          next_callback=self.go_next,
                          defaults=page4_defaults)
            self.stacked.addWidget(page4)
            self.pages.append(page4)

            # Show Page1
            self.stacked.setCurrentIndex(1)

        except Exception as ex:
            # Show the traceback so you can see what failed
            import traceback
            tb = traceback.format_exc()
            print("handle_page0_next error:\n", tb)
            QMessageBox.critical(self, "Error creating pages",
                                 f"An error occurred while creating pages:\n\n{str(ex)}\n\nSee console for full traceback.")

    def go_prev(self):
        idx = self.stacked.currentIndex()
        if idx > 0:
            self.stacked.setCurrentIndex(idx - 1)

    def run_terminal_simulation(self):
        """Collects all user inputs and runs the full simulation."""
        print("Running full simulation...")

        """Collects all user inputs and runs the full simulation."""
        print("Running full simulation...")

        # --- Page0 ---
        page0 = self.pages[0]
        try:
            num_servers = int(page0.num_field.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Number of servers must be a valid integer.")
            return

        # If you have a 'number of users' field on another page (e.g. Page3), you can get it there.
        # For now, let’s assume it’s from Page3:
        page3 = self.pages[-2]  # Page3 is second last before Page4
        try:
            num_users = int(page3.num_instances_field.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Number of users must be a valid integer.")
            return

        # --- Page1 (Interarrival) ---
        page1 = self.pages[1]
        interarrival_start = page1.start_val
        interarrival_end = page1.end_val
        interarrival_probabilities = page1.probs_val

        # --- Page2 list (Service Times for each server) ---
        start_list = []
        end_list = []
        prob_list = []
        priority_list = []

        # You already know: Page2 repeats once per server
        # (Page indices: Page2 starts at 2 → up to 2 + num_servers - 1)
        for i in range(num_servers):
            page2 = self.pages[2 + i]
            start_list.append(page2.start_val)
            end_list.append(page2.end_val)
            prob_list.append(page2.probs_val)
            # Optional: if each Page2 has priority dropdown or field, fetch it here
            if hasattr(page2, "priority_field"):
                priority_list.append(page2.priority_field.currentText())
            else:
                priority_list.append(f"Server {i + 1}")

        # --- Page3 (Priority Rules, if exists) ---
        if len(self.pages) > (2 + num_servers):
            page3 = self.pages[2 + num_servers]
            if hasattr(page3, "priority_field"):
                # Example: user chooses priority for each server
                priority_list = [page3.priority_field.currentText()] * num_servers

        # --- Now call the actual simulation ---
        try:
            result = Algorithm.run_full_simulation(
                num_users=num_users,
                interarrival_start=interarrival_start,
                interarrival_end=interarrival_end,
                interarrival_probabilities=interarrival_probabilities,
                num_servers=num_servers,
                priority_list=priority_list,
                start_list=start_list,
                end_list=end_list,
                prob_list=prob_list,
            )

            # Optional: print or display results
            print("Simulation complete! Results:")
            print(result)

        except Exception as e:
            QMessageBox.critical(self, "Simulation Error", f"An error occurred:\n{str(e)}")

    def run_txt_report_simulation(self):
        """Collects all user inputs, runs the full simulation, and saves a .txt report."""
        print("Running full simulation and saving to TXT...")

        # --- Page0 ---
        page0 = self.pages[0]
        try:
            num_servers = int(page0.num_field.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Number of servers must be a valid integer.")
            return

        # --- Page3 (Users) ---
        page3 = self.pages[-2]  # second last page before results
        try:
            num_users = int(page3.num_instances_field.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Number of users must be a valid integer.")
            return

        # --- Page1 (Interarrival) ---
        page1 = self.pages[1]
        interarrival_start = page1.start_val
        interarrival_end = page1.end_val
        interarrival_probabilities = page1.probs_val

        # --- Page2 list (Service Times per Server) ---
        start_list, end_list, prob_list, priority_list = [], [], [], []
        for i in range(num_servers):
            page2 = self.pages[2 + i]
            start_list.append(page2.start_val)
            end_list.append(page2.end_val)
            prob_list.append(page2.probs_val)
            if hasattr(page2, "priority_field"):
                priority_list.append(page2.priority_field.currentText())
            else:
                priority_list.append(f"Server {i + 1}")

        # --- Page3 (optional Priority Rules) ---
        if len(self.pages) > (2 + num_servers):
            page3 = self.pages[2 + num_servers]
            if hasattr(page3, "priority_field"):
                priority_list = [page3.priority_field.currentText()] * num_servers

        # --- Run the simulation ---
        try:
            # 1️⃣ Prepare input tables
            interarrival_dist_table, interarrival_assigned_table, servers_dist_tables = \
                Algorithm.prepare_simulation_inputs(
                    interarrival_start, interarrival_end, interarrival_probabilities,
                    num_servers, start_list, end_list, prob_list
                )

            # 2️⃣ Run queue simulation
            simulation_result = Algorithm.simulate_queue(
                interarrival_dist_table,
                interarrival_assigned_table,
                servers_dist_tables,
                num_users
            )

            # 3️⃣ Save to TXT
            Algorithm.save_queue_report_to_txt(
                simulation_result,
                interarrival_dist_table,
                interarrival_assigned_table,
                servers_dist_tables
            )

            QMessageBox.information(
                self,
                "Report Saved",
                "✅ Simulation complete!\nA detailed TXT report has been generated in your project folder."
            )

        except Exception as e:
            QMessageBox.critical(self, "Simulation Error", f"An error occurred:\n{str(e)}")

    def go_next(self):
        idx = self.stacked.currentIndex()
        current_page = self.pages[idx]
        if isinstance(current_page, (Page1, Page2)):
            try:
                start = int(current_page.start_field.text())
                end = int(current_page.end_field.text())
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Start and End must be numbers.")
                return

            # ✅ If "Equal Probabilities" is checked, skip validation and auto-generate equal probabilities
            if current_page.equal_checkbox.isChecked():
                num_items = end - start + 1
                probs = [1 / num_items] * num_items
                current_page.start_val = start
                current_page.end_val = end
                current_page.probs_val = probs
                # Skip any probability field checks entirely
                # Just go to next page
            else:
                # --- Manual Probability Input Validation ---
                probs_text = current_page.prob_field.text().strip()
                prob_items = [x for x in probs_text.split() if x]
                try:
                    probs = [float(x) for x in prob_items]
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", "Probabilities must be numbers separated by spaces.")
                    return

                if len(prob_items) != (end - start + 1):
                    QMessageBox.warning(
                        self,
                        "Invalid Input",
                        f"Number of probabilities must be equal to end-start+1 ({end - start + 1}).",
                    )
                    return

                if abs(sum(probs) - 1.0) > 1e-6:
                    QMessageBox.warning(self, "Invalid Input", "Sum of probabilities must equal 1.")
                    return

                current_page.start_val = start
                current_page.end_val = end
                current_page.probs_val = probs

        # --- Page4 Handling ---
        elif isinstance(current_page, Page4):
            selected = current_page.selected_option()
            if not selected:
                QMessageBox.warning(self, "No Option Selected", "Please choose an output option first.")
                return

            if selected == "Excel":
                print("Exporting results to Excel...")
                # TODO: call your export-to-Excel function here

            elif selected == "Text File":
                self.run_txt_report_simulation()
                # TODO: show a results window or dialog here

            elif selected == "Terminal":

                print("Running terminal output commands...")
                self.run_terminal_simulation()

        # --- Go next or finish ---
        if idx < self.stacked.count() - 1:
            self.stacked.setCurrentIndex(idx + 1)
        else:
            # Handle Page4 output
            page4 = self.pages[-1]
            selected = page4.selected_option()
            if not selected:
                QMessageBox.warning(self, "No Option Selected", "Please choose an output option first.")
                return
            print("Output option selected:", selected)
            self.close()

    ######################################################################################################################################################

    def mousePressEvent(self, event):
        self._drag_pos = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

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

    ######################################################################################################################################################
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Third Assignment")
        self.setFixedSize(310, 557)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.center_on_screen()

        central = QWidget()
        central.setStyleSheet("""
            background-color: #4C4C4C;
            border-radius: 25px;
        """)
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Default data holder
        self.input_data = {
            "page1": {},
            "page2_list": [],
            "page3": {},
            "page4": {}
        }

        # Stacked widget
        self.stacked = QStackedWidget()

        # Add Page0 first (pass BOTH callbacks)
        self.page0 = Page0(prev_callback=self.handle_back, next_callback=self.handle_page0_next)
        self.stacked.addWidget(self.page0)

        main_layout.addWidget(self.stacked)
        central.setLayout(main_layout)

        # Store references to pages
        self.pages = [self.page0]

    def handle_back(self):
        idx = self.stacked.currentIndex()

        # If on Page0 → go back to Dashboard
        if idx == 0:
            from MAIN import DashboardWindow  # adjust import if needed
            self.dashboard = DashboardWindow()
            self.dashboard.show()
            self.close()
            return

        # Otherwise go back to previous page
        if idx > 0:
            self.stacked.setCurrentIndex(idx - 1)


######################################################################################################################################################

class Page1(BasePage):
    def __init__(self, prev_callback=None, next_callback=None, defaults=None):
        super().__init__()

        defaults = defaults or {}

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

        self.start_field = self.make_field("Start")
        self.start_field.setText(str(defaults.get("start", "1")))
        self.start_field.setValidator(QIntValidator(1, 10000))


        self.end_field = self.make_field("End")
        self.end_field.setText(str(defaults.get("end", "5")))
        self.end_field.setValidator(QIntValidator(1, 10000))

        range_row = QHBoxLayout()
        range_row.addWidget(range_label)
        range_row.addStretch()
        range_row.addWidget(self.start_field)
        range_row.addWidget(self.end_field)
        self.main_layout.addLayout(range_row)

        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy  .Minimum, QSizePolicy.Fixed))

        # --- Equal section ---
        self.equal_checkbox = QCheckBox("Equal")
        self.equal_checkbox.setStyleSheet("color: white;")
        equal_text = QLabel("All probabilities are the same")
        equal_text.setStyleSheet("color: gray; font-size: 12px;")
        equal_text.setWordWrap(True)
        self.equal_checkbox.setChecked(defaults.get("equal", True))
        self.main_layout.addWidget(self.equal_checkbox)
        self.main_layout.addWidget(equal_text)
        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- Probabilities section ---
        prob_label = QLabel("Probabilities")
        prob_label.setStyleSheet("color: white; font-size: 14px;")
        self.prob_field = self.make_field("Sum of xProbs. must equal 1", width=200, height=40)
        self.prob_field.setText(defaults.get("probabilities", "0.2 0.2 0.2 0.2 0.2"))


        regex = QRegularExpression(r"^(\d*\.?\d+\s*)+$")
        validator = QRegularExpressionValidator(regex)
        self.prob_field.setValidator(validator)
        self.main_layout.addWidget(prob_label)
        self.main_layout.addWidget(self.prob_field)

        # Push everything up
        self.main_layout.addStretch()

        # --- Range section ---
        NOS = QLabel("Number of Servers")
        NOS.setStyleSheet("color: white; font-size: 14px;")

        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- Nav buttons at bottom ---
        self.main_layout.addLayout(self.nav_layout)
        self.add_nav_buttons(prev_callback, next_callback)

###########################################################################

class Page2(BasePage):
    def __init__(self, prev_callback=None, next_callback=None, defaults=None):
        super().__init__()

        defaults = defaults or {}

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

        self.start_field = self.make_field("Start")
        self.start_field.setText(str(defaults.get("start", "")))
        self.start_field.setValidator(QIntValidator(1, 10000))

        self.end_field = self.make_field("End")
        self.end_field.setText(str(defaults.get("end", "")))
        self.end_field.setValidator(QIntValidator(1, 10000))

        range_row = QHBoxLayout()
        range_row.addWidget(range_label)
        range_row.addStretch()
        range_row.addWidget(self.start_field)
        range_row.addWidget(self.end_field)
        self.main_layout.addLayout(range_row)

        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- Equal section ---
        self.equal_checkbox = QCheckBox("Equal")
        self.equal_checkbox.setStyleSheet("color: white;")
        equal_text = QLabel("All probabilities are the same")
        equal_text.setStyleSheet("color: gray; font-size: 12px;")
        equal_text.setWordWrap(True)
        self.equal_checkbox.setChecked(defaults.get("equal", False))
        self.main_layout.addWidget(self.equal_checkbox)
        self.main_layout.addWidget(equal_text)
        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- Probabilities section ---
        prob_label = QLabel("Probabilities")
        prob_label.setStyleSheet("color: white; font-size: 14px;")
        self.prob_field = self.make_field("Sum of Probs. must equal 1", width=200, height=40)
        self.prob_field.setText(defaults.get("probabilities", ""))

        regex = QRegularExpression(r"^(\d*\.?\d+\s*)+$")
        validator = QRegularExpressionValidator(regex)
        self.prob_field.setValidator(validator)
        self.main_layout.addWidget(prob_label)
        self.main_layout.addWidget(self.prob_field)

        # Bottom stretch
        self.main_layout.addStretch()

        # --- Nav buttons at bottom ---
        self.main_layout.addLayout(self.nav_layout)
        self.add_nav_buttons(prev_callback, next_callback)

###########################################################################
class Page3(BasePage):
    def __init__(self, prev_callback=None, next_callback=None, defaults=None):
        super().__init__()
        defaults = defaults or {}

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

        self.main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- How Many Instances ---
        range_label = QLabel("How Many Instances")
        range_label.setStyleSheet("color: white; font-size: 14px;")

        self.num_instances_field = self.make_field("Ex.20")
        self.num_instances_field.setValidator(QIntValidator(1, 10000))
        self.num_instances_field.setText(str(defaults.get("instances", 20)))  # default = 20

        range_row = QHBoxLayout()
        range_row.addWidget(range_label)
        range_row.addStretch()
        range_row.addWidget(self.num_instances_field)
        self.main_layout.addLayout(range_row)

        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- Radio section ---
        self.traffic_radio = QRadioButton("Traffic")
        self.traffic_radio.setChecked(defaults.get("traffic_selected", True))
        self.traffic_radio.setStyleSheet("color: white;")

        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.traffic_radio)
        radio_layout.addStretch()
        self.main_layout.addLayout(radio_layout)

        # Bottom stretch
        self.main_layout.addStretch()

        # --- Nav buttons ---
        self.main_layout.addLayout(self.nav_layout)
        self.add_nav_buttons(prev_callback, next_callback)

###########################################################################

class Page4(BasePage):
    def selected_option(self):
        checked_button = self.button_group.checkedButton()
        return checked_button.text() if checked_button else None

    def __init__(self, prev_callback=None, next_callback=None, defaults=None):
        super().__init__()
        defaults = defaults or {}

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
            ("Excel", "Export results to an Excel (.xlsx) file"),
            ("Text File", "Display results inside text file (.txt) file"),
            ("Terminal", "Print results in the console output")
        ]

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.radio_buttons = []

        default_selected = defaults.get("output_option", None)

        for label_text, description in options:
            radio = QRadioButton(label_text)
            radio.setStyleSheet("color: white; font-size: 14px;")
            self.button_group.addButton(radio)
            self.main_layout.addWidget(radio)

            # If this matches default, select it
            if label_text == default_selected:
                radio.setChecked(True)

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
