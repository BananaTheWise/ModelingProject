import csv
import os
import json
import sqlite3
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel,
    QHBoxLayout, QStackedWidget, QSpacerItem, QSizePolicy, QMessageBox,
    QApplication, QRadioButton, QButtonGroup, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator

from MAIN import DashboardWindow
from GUI.Basics import BasePage
from ALGORITHMS.Fifth import run_event_scheduling_simulation

class FifthAssignment(QMainWindow):

    def go_prev(self):
        idx = self.stacked.currentIndex()
        if idx > 0:
            self.stacked.setCurrentIndex(idx - 1)

    def go_next(self):
        idx = self.stacked.currentIndex()
        current_page = self.pages[idx]

        try:
            if isinstance(current_page, Page1):
                self.input_data["num_customers"] = int(current_page.num_customers_field.text())
                self.input_data["stop_time"] = int(current_page.stop_time_field.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please ensure all fields are filled with valid integers.")
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            return

        if idx < self.stacked.count() - 1:
            self.stacked.setCurrentIndex(idx + 1)
        else:
            self.handle_output()

    def handle_output(self):
        selected_option = self.pages[1].get_selected_option()
        if not selected_option:
            QMessageBox.warning(self, "No Selection", "Please select an output option.")
            return
            
        if selected_option == "Exit":
            self.close()
            return

        results = run_event_scheduling_simulation(
            num_customers=self.input_data["num_customers"],
            stop_time=self.input_data["stop_time"]
        )
        
        event_table = results['event_table']
        simulation_table = results['simulation_table']
        statistics = results['statistics']

        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if selected_option == "Terminal":
            self.output_to_terminal(event_table, simulation_table, statistics)
        elif selected_option == "GUI":
            self.output_to_gui(event_table, simulation_table, statistics)
        elif selected_option == "Excel":
            self.output_to_csv(event_table, simulation_table, statistics, output_dir)
        elif selected_option == "txt":
            self.output_to_txt(event_table, simulation_table, statistics, output_dir)
        elif selected_option == "JSON":
            self.output_to_json(event_table, simulation_table, statistics, output_dir)
        elif selected_option == "SQLite":
            self.output_to_sqlite(event_table, simulation_table, statistics, output_dir)

    def _format_table_to_string(self, table_data, title, is_dict=False):
        if not table_data: return ""
        
        if is_dict:
            table_data = [{"Parameter": k, "Value": v} for k, v in table_data.items()]

        headers = table_data[0].keys()
        col_widths = {h: max(len(str(h)), max(len(str(row[h])) for row in table_data)) for h in headers}
        
        header_line = " | ".join(f"{h:<{col_widths[h]}}" for h in headers)
        separator = "-+-".join("-" * col_widths[h] for h in headers)
        rows_lines = [" | ".join(f"{str(row[h]):<{col_widths[h]}}" for h in headers) for row in table_data]
            
        return f"--- {title} ---\n{header_line}\n{separator}\n" + "\n".join(rows_lines) + "\n"

    def output_to_terminal(self, event_table, simulation_table, statistics):
        print(self._format_table_to_string(statistics, "Final Statistics", is_dict=True))
        print(self._format_table_to_string(event_table, "Event Table"))
        print(self._format_table_to_string(simulation_table, "Simulation Log"))
        QMessageBox.information(self, "Output", "Results printed to terminal.")

    def output_to_txt(self, event_table, simulation_table, statistics, output_dir):
        path = os.path.join(output_dir, "eventsim_output.txt")
        try:
            with open(path, "w") as f:
                f.write(self._format_table_to_string(statistics, "Final Statistics", is_dict=True))
                f.write(self._format_table_to_string(event_table, "Event Table"))
                f.write(self._format_table_to_string(simulation_table, "Simulation Log"))
            QMessageBox.information(self, "Success", f"Output saved to {os.path.abspath(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not write to TXT file: {e}")

    def output_to_csv(self, event_table, simulation_table, statistics, output_dir):
        path = os.path.join(output_dir, "eventsim_output.csv")
        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                
                writer.writerow(["--- Final Statistics ---"])
                writer.writerow(statistics.keys())
                writer.writerow(statistics.values())
                writer.writerow([])

                def write_table(title, data):
                    writer.writerow([f"--- {title} ---"])
                    if not data: return
                    writer.writerow(data[0].keys())
                    writer.writerows([row.values() for row in data])
                    writer.writerow([])
                
                write_table("Event Table", event_table)
                write_table("Simulation Log", simulation_table)

            QMessageBox.information(self, "Success", f"Output saved to {os.path.abspath(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not write to CSV file: {e}")

    def output_to_json(self, event_table, simulation_table, statistics, output_dir):
        path = os.path.join(output_dir, "eventsim_output.json")
        output_data = {
            "statistics": statistics,
            "event_table": event_table,
            "simulation_log": simulation_table,
        }
        try:
            with open(path, "w") as f:
                json.dump(output_data, f, indent=4)
            QMessageBox.information(self, "Success", f"Output saved to {os.path.abspath(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not write to JSON file: {e}")

    def output_to_sqlite(self, event_table, simulation_table, statistics, output_dir):
        path = os.path.join(output_dir, "eventsim_output.db")
        try:
            if os.path.exists(path): os.remove(path)
            conn = sqlite3.connect(path)
            
            import pandas as pd
            pd.DataFrame([statistics]).to_sql('statistics', conn, index=False, if_exists='replace')
            if event_table:
                pd.DataFrame(event_table).to_sql('event_table', conn, index=False, if_exists='replace')
            if simulation_table:
                pd.DataFrame(simulation_table).to_sql('simulation_log', conn, index=False, if_exists='replace')
            
            conn.close()
            QMessageBox.information(self, "Success", f"Output saved to {os.path.abspath(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not write to SQLite file: {e}. Make sure 'pandas' is installed (`pip install pandas`).")

    def output_to_gui(self, event_table, simulation_table, statistics):
        self.output_window = OutputWindow(event_table, simulation_table, statistics)
        self.output_window.show()

    def mousePressEvent(self, event):
        self._drag_pos = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def center_on_screen(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Single Server Simulation")
        self.setFixedSize(310, 557)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.center_on_screen()

        central = QWidget()
        central.setStyleSheet("background-color: #4C4C4C; border-radius: 25px;")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.input_data = {"num_customers": 5, "stop_time": 50}

        self.stacked = QStackedWidget()
        self.pages = [
            Page1(prev_callback=self.handle_back, next_callback=self.go_next, defaults=self.input_data),
            Page2(prev_callback=self.go_prev, next_callback=self.handle_output),
        ]

        for page in self.pages:
            self.stacked.addWidget(page)

        main_layout.addWidget(self.stacked)

    def handle_back(self):
        if self.stacked.currentIndex() == 0:
            self.dashboard = DashboardWindow()
            self.dashboard.show()
            self.close()
        else:
            self.go_prev()

class Page1(BasePage):
    def __init__(self, prev_callback=None, next_callback=None, defaults=None):
        super().__init__()
        defaults = defaults or {}
        self.main_layout.addLayout(self.centered_row(self.create_title("Simulation Inputs", width=200)))
        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        self.num_customers_field = self._create_input_row(form_layout, "Number of Customers:", "(e.g., 5)", str(defaults.get("num_customers", "")))
        self.stop_time_field = self._create_input_row(form_layout, "Simulation Stop Time:", "(e.g., 50)", str(defaults.get("stop_time", "")))
        
        self.num_customers_field.setValidator(QIntValidator(1, 10000))
        self.stop_time_field.setValidator(QIntValidator(1, 100000))

        self.main_layout.addLayout(form_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.nav_layout)
        self.add_nav_buttons(prev_callback, next_callback, prev_text="Back to Main", next_text="Next to Outputs")

class Page2(BasePage):
    def __init__(self, prev_callback=None, next_callback=None):
        super().__init__()
        self.main_layout.addLayout(self.centered_row(self.create_title("Output Options")))
        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        self.button_group = QButtonGroup(self)
        options = ["Terminal", "GUI", "Excel", "txt", "JSON", "SQLite", "Exit"]
        for option in options:
            radio_button = QRadioButton(option)
            radio_button.setStyleSheet("""
                QRadioButton { color: white; font-size: 14px; }
                QRadioButton::indicator { border: 2px solid #CDCDCD; border-radius: 9px; width: 15px; height: 15px; background-color: #4C4C4C; }
                QRadioButton::indicator:checked { background-color: #61AF5E; border: 2px solid #F5F5F5; }
            """)
            self.main_layout.addWidget(radio_button)
            self.button_group.addButton(radio_button)

        self.main_layout.addStretch()
        self.main_layout.addLayout(self.nav_layout)
        self.add_nav_buttons(prev_callback, next_callback, prev_text="Back to Inputs", next_text="Show Results")

    def get_selected_option(self):
        checked_button = self.button_group.checkedButton()
        return checked_button.text() if checked_button else None

class OutputWindow(QMainWindow):
    def __init__(self, event_table, simulation_table, statistics):
        super().__init__()
        self.setWindowTitle("Single Server Simulation Output")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("background-color: #4C4C4C; color: white;")

        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #888888; }
            QTabBar::tab { background: #2C2C2C; color: white; padding: 10px; border: 1px solid #888888; border-bottom: none; }
            QTabBar::tab:selected { background: #4C4C4C; border-bottom: 1px solid #4C4C4C; }
        """)
        self.setCentralWidget(tab_widget)

        tab_widget.addTab(self.create_table(statistics, is_dict=True), "Final Statistics")
        tab_widget.addTab(self.create_table(event_table), "Event Table")
        tab_widget.addTab(self.create_table(simulation_table), "Simulation Log")

    def create_table(self, data, is_dict=False):
        if is_dict:
            table_data = list(data.items())
            table = QTableWidget(len(table_data), 2)
            table.setHorizontalHeaderLabels(["Statistic", "Value"])
            for i, (key, value) in enumerate(table_data):
                table.setItem(i, 0, QTableWidgetItem(str(key)))
                table.setItem(i, 1, QTableWidgetItem(str(value)))
        else:
            if not data: return QTableWidget()
            table = QTableWidget(len(data), len(data[0]))
            table.setHorizontalHeaderLabels(data[0].keys())
            for i, row_data in enumerate(data):
                for j, value in enumerate(row_data.values()):
                    table.setItem(i, j, QTableWidgetItem(str(value)))
        
        table.setStyleSheet("""
            QTableWidget { background-color: #2C2C2C; color: white; gridline-color: #888888; alternate-background-color: #3C3C3C; }
            QHeaderView::section { background-color: #61AF5E; color: black; padding: 4px; border: 1px solid #2C2C2C; }
        """)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table
