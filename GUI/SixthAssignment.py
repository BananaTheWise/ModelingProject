import csv
import os
import json
import sqlite3
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QHBoxLayout,
    QStackedWidget,
    QSpacerItem,
    QSizePolicy,
    QMessageBox,
    QApplication,
    QRadioButton,
    QButtonGroup,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QCheckBox,
    QTabWidget,
)
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

from MAIN import DashboardWindow
from GUI.Basics import BasePage
from ALGORITHMS.Sixth import newspaper_simulation

matplotlib.use('QtAgg')


class SixthAssignment(QMainWindow):

    def go_prev(self):
        idx = self.stacked.currentIndex()
        if idx > 0:
            self.stacked.setCurrentIndex(idx - 1)

    def go_next(self):
        idx = self.stacked.currentIndex()
        current_page = self.pages[idx]

        try:
            if isinstance(current_page, Page1):
                self.input_data["page1"]["buy_price"] = float(current_page.buy_price_field.text())
                self.input_data["page1"]["sell_price"] = float(current_page.sell_price_field.text())
                self.input_data["page1"]["scrap_price"] = float(current_page.scrap_price_field.text())
                self.input_data["page1"]["num_newspapers"] = int(current_page.num_newspapers_field.text())
                self.input_data["page1"]["num_days"] = int(current_page.num_days_field.text())

            elif isinstance(current_page, Page2):
                prob_good = float(current_page.prob_good_field.text())
                prob_fair = float(current_page.prob_fair_field.text())
                prob_poor = float(current_page.prob_poor_field.text())
                if abs(prob_good + prob_fair + prob_poor - 1.0) > 1e-6:
                    QMessageBox.warning(self, "Invalid Input", "Probabilities for Good, Fair, and Poor must sum to 1.")
                    return
                self.input_data["page2"]["prob_good"] = prob_good
                self.input_data["page2"]["prob_fair"] = prob_fair
                self.input_data["page2"]["prob_poor"] = prob_poor

            elif isinstance(current_page, Page3):
                start = int(current_page.start_demand_field.text())
                end = int(current_page.end_demand_field.text())
                num_demands = end - start + 1

                if current_page.equal_good_checkbox.isChecked():
                    good_probs = [1 / num_demands] * num_demands
                else:
                    good_probs = [float(p) for p in current_page.prob_good_demand_field.text().strip().split()]
                    if len(good_probs) != num_demands or abs(sum(good_probs) - 1.0) > 1e-6:
                        QMessageBox.warning(self, "Invalid Input", "Good day probabilities are invalid.")
                        return
                
                if current_page.equal_fair_checkbox.isChecked():
                    fair_probs = [1 / num_demands] * num_demands
                else:
                    fair_probs = [float(p) for p in current_page.prob_fair_demand_field.text().strip().split()]
                    if len(fair_probs) != num_demands or abs(sum(fair_probs) - 1.0) > 1e-6:
                        QMessageBox.warning(self, "Invalid Input", "Fair day probabilities are invalid.")
                        return

                if current_page.equal_poor_checkbox.isChecked():
                    poor_probs = [1 / num_demands] * num_demands
                else:
                    poor_probs = [float(p) for p in current_page.prob_poor_demand_field.text().strip().split()]
                    if len(poor_probs) != num_demands or abs(sum(poor_probs) - 1.0) > 1e-6:
                        QMessageBox.warning(self, "Invalid Input", "Poor day probabilities are invalid.")
                        return

                self.input_data["page3"]["start_demand"] = start
                self.input_data["page3"]["end_demand"] = end
                self.input_data["page3"]["prob_good_demand"] = good_probs
                self.input_data["page3"]["prob_fair_demand"] = fair_probs
                self.input_data["page3"]["prob_poor_demand"] = poor_probs

        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please ensure all fields are filled with valid numbers.")
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            return

        if idx < self.stacked.count() - 1:
            self.stacked.setCurrentIndex(idx + 1)
        else:
            self.handle_output()

    def handle_output(self):
        selected_option = self.pages[3].get_selected_option()
        if not selected_option:
            QMessageBox.warning(self, "No Selection", "Please select an output option.")
            return
            
        if selected_option == "Exit":
            self.close()
            return

        p1 = self.input_data["page1"]
        p2 = self.input_data["page2"]
        p3 = self.input_data["page3"]

        results = newspaper_simulation(
            buy_price=p1["buy_price"], sell_price=p1["sell_price"], scrap_price=p1["scrap_price"],
            num_newspapers=p1["num_newspapers"], num_days=p1["num_days"],
            prob_good=p2["prob_good"], prob_fair=p2["prob_fair"], prob_poor=p2["prob_poor"],
            start_demand=p3["start_demand"], end_demand=p3["end_demand"],
            prob_good_demand=p3["prob_good_demand"], prob_fair_demand=p3["prob_fair_demand"], prob_poor_demand=p3["prob_poor_demand"]
        )
        
        input_params, demand_table, type_table, simulation_table, metrics = results

        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if selected_option == "Terminal":
            self.output_to_terminal(input_params, demand_table, type_table, simulation_table, metrics)
        elif selected_option == "gui":
            self.output_to_gui(input_params, demand_table, type_table, simulation_table, metrics)
        elif selected_option == "Excel":
            self.output_to_csv(input_params, demand_table, type_table, simulation_table, metrics, output_dir)
        elif selected_option == "txt":
            self.output_to_txt(input_params, demand_table, type_table, simulation_table, metrics, output_dir)
        elif selected_option == "JSON":
            self.output_to_json(input_params, demand_table, type_table, simulation_table, metrics, output_dir)
        elif selected_option == "SQLite":
            self.output_to_sqlite(input_params, demand_table, type_table, simulation_table, metrics, output_dir)
        elif selected_option == "graph":
            self.output_to_graph(simulation_table)

    def _format_table_to_string(self, table_data, title):
        if not table_data: return ""
        
        formatted_data = []
        for row in table_data:
            new_row = {}
            for key, value in row.items():
                if isinstance(value, float):
                    new_row[key] = f"{value:.2f}"
                else:
                    new_row[key] = str(value)
            formatted_data.append(new_row)

        headers = formatted_data[0].keys()
        
        try:
            col_widths = {h: max(len(h), max(len(row[h]) for row in formatted_data)) for h in headers}
        except ValueError:
            return ""

        header_line = " | ".join(f"{h:<{col_widths[h]}}" for h in headers)
        separator = "-+-".join("-" * col_widths[h] for h in headers)
        
        rows_lines = [ " | ".join(f"{row[h]:<{col_widths[h]}}" for h in headers) for row in formatted_data ]
            
        return f"--- {title} ---\n{header_line}\n{separator}\n" + "\n".join(rows_lines) + "\n"

    def output_to_terminal(self, input_params, demand_table, type_table, simulation_table, metrics):
        print(self._format_table_to_string([input_params], "Input Parameters"))
        print(self._format_table_to_string(demand_table, "Demand Distribution"))
        print(self._format_table_to_string(type_table, "Day Type Distribution"))
        print(self._format_table_to_string(simulation_table, "Simulation Log"))
        print(self._format_table_to_string([metrics], "Final Metrics"))
        QMessageBox.information(self, "Output", "Results printed to terminal.")

    def output_to_txt(self, input_params, demand_table, type_table, simulation_table, metrics, output_dir):
        path = os.path.join(output_dir, "newspaper_simulation_output.txt")
        try:
            with open(path, "w") as f:
                f.write(self._format_table_to_string([input_params], "Input Parameters"))
                f.write(self._format_table_to_string(demand_table, "Demand Distribution"))
                f.write(self._format_table_to_string(type_table, "Day Type Distribution"))
                f.write(self._format_table_to_string(simulation_table, "Simulation Log"))
                f.write(self._format_table_to_string([metrics], "Final Metrics"))
            QMessageBox.information(self, "Success", f"Output saved to {os.path.abspath(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not write to TXT file: {e}")

    def output_to_csv(self, input_params, demand_table, type_table, simulation_table, metrics, output_dir):
        path = os.path.join(output_dir, "newspaper_simulation_output.csv")
        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                def write_table(title, data):
                    writer.writerow([f"--- {title} ---"])
                    if not data: return
                    writer.writerow(data[0].keys())
                    for row in data:
                        writer.writerow(row.values())
                    writer.writerow([])
                
                write_table("Input Parameters", [input_params])
                write_table("Demand Distribution", demand_table)
                write_table("Day Type Distribution", type_table)
                write_table("Simulation Log", simulation_table)
                write_table("Final Metrics", [metrics])
            QMessageBox.information(self, "Success", f"Output saved to {os.path.abspath(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not write to CSV file: {e}")

    def output_to_json(self, input_params, demand_table, type_table, simulation_table, metrics, output_dir):
        path = os.path.join(output_dir, "newspaper_simulation_output.json")
        output_data = {
            "input_parameters": input_params,
            "demand_distribution": demand_table,
            "day_type_distribution": type_table,
            "simulation_log": simulation_table,
            "final_metrics": metrics
        }
        try:
            with open(path, "w") as f:
                json.dump(output_data, f, indent=4)
            QMessageBox.information(self, "Success", f"Output saved to {os.path.abspath(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not write to JSON file: {e}")

    def output_to_sqlite(self, input_params, demand_table, type_table, simulation_table, metrics, output_dir):
        path = os.path.join(output_dir, "newspaper_simulation_output.db")
        try:
            if os.path.exists(path): os.remove(path)
            conn = sqlite3.connect(path)
            def write_to_db(table_name, data):
                if not data: return
                import pandas as pd
                df = pd.DataFrame(data)
                df.to_sql(table_name, conn, index=False, if_exists='replace')

            write_to_db('input_parameters', [input_params])
            write_to_db('demand_distribution', demand_table)
            write_to_db('day_type_distribution', type_table)
            write_to_db('simulation_log', simulation_table)
            write_to_db('final_metrics', [metrics])
            
            conn.close()
            QMessageBox.information(self, "Success", f"Output saved to {os.path.abspath(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not write to SQLite file: {e}. Make sure 'pandas' is installed (`pip install pandas`).")

    def output_to_gui(self, input_params, demand_table, type_table, simulation_table, metrics):
        self.output_window = OutputWindow(input_params, demand_table, type_table, simulation_table, metrics)
        self.output_window.show()

    def output_to_graph(self, simulation_log):
        self.graph_window = GraphOutputWindow(simulation_log)
        self.graph_window.show()

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
        self.setWindowTitle("Newspaper Simulation")
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

        self.input_data = {
            "page1": {"buy_price": 0.33, "sell_price": 1.50, "scrap_price": 0.05, "num_newspapers": 10, "num_days": 10},
            "page2": {"prob_good": 0.35, "prob_fair": 0.45, "prob_poor": 0.20},
            "page3": {"start_demand": 8, "end_demand": 12, 
                      "prob_good_demand": [0.03, 0.05, 0.15, 0.20, 0.57],
                      "prob_fair_demand": [0.10, 0.18, 0.40, 0.20, 0.12],
                      "prob_poor_demand": [0.44, 0.22, 0.16, 0.12, 0.06]}
        }

        self.stacked = QStackedWidget()
        self.pages = [
            Page1(prev_callback=self.handle_back, next_callback=self.go_next, defaults=self.input_data["page1"]),
            Page2(prev_callback=self.go_prev, next_callback=self.go_next, defaults=self.input_data["page2"]),
            Page3(prev_callback=self.go_prev, next_callback=self.go_next, defaults=self.input_data["page3"]),
            Page4(prev_callback=self.go_prev, next_callback=self.go_next),
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
        self.main_layout.addLayout(self.centered_row(self.create_title("Newspaper - Inputs", width=200)))
        self.main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        self.buy_price_field = self._create_input_row(form_layout, "Buy Price:", "(ex. 0.33)", str(defaults.get("buy_price", "")))
        self.sell_price_field = self._create_input_row(form_layout, "Sell Price:", "(ex. 1.50)", str(defaults.get("sell_price", "")))
        self.scrap_price_field = self._create_input_row(form_layout, "Scrap Price:", "(ex. 0.05)", str(defaults.get("scrap_price", "")))
        self.num_newspapers_field = self._create_input_row(form_layout, "Newspapers Purchased:", "(ex. 10)", str(defaults.get("num_newspapers", "")))
        self.num_days_field = self._create_input_row(form_layout, "Number of Days:", "(ex. 10)", str(defaults.get("num_days", "")))
        
        for field in [self.buy_price_field, self.sell_price_field, self.scrap_price_field]:
            field.setValidator(QDoubleValidator(0, 10000, 2))
        for field in [self.num_newspapers_field, self.num_days_field]:
            field.setValidator(QIntValidator(0, 1000000))

        self.main_layout.addLayout(form_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.nav_layout)
        self.add_nav_buttons(prev_callback, next_callback, prev_text="Back to Main", next_text="Next to Page 2")

class Page2(BasePage):
    def __init__(self, prev_callback=None, next_callback=None, defaults=None):
        super().__init__()
        defaults = defaults or {}
        self.main_layout.addLayout(self.centered_row(self.create_title("Newspaper - Day Type")))
        self.main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        self.prob_good_field = self._create_input_row(form_layout, "Prob. of Good Day:", "(ex. 0.35)", str(defaults.get("prob_good", "")))
        self.prob_fair_field = self._create_input_row(form_layout, "Prob. of Fair Day:", "(ex. 0.45)", str(defaults.get("prob_fair", "")))
        self.prob_poor_field = self._create_input_row(form_layout, "Prob. of Poor Day:", "(ex. 0.20)", str(defaults.get("prob_poor", "")))
        
        for field in [self.prob_good_field, self.prob_fair_field, self.prob_poor_field]:
            field.setValidator(QDoubleValidator(0, 1, 2))

        self.main_layout.addLayout(form_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.nav_layout)
        self.add_nav_buttons(prev_callback, next_callback, prev_text="Back to Page 1", next_text="Next to Page 3")

class Page3(BasePage):
    def __init__(self, prev_callback=None, next_callback=None, defaults=None):
        super().__init__()
        defaults = defaults or {}
        self.main_layout.addLayout(self.centered_row(self.create_title("Newspaper - Demand")))
        self.main_layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("Demand Range:"))
        self.start_demand_field = self.make_field("Start", width=50)
        self.start_demand_field.setText(str(defaults.get("start_demand", "")))
        self.end_demand_field = self.make_field("End", width=50)
        self.end_demand_field.setText(str(defaults.get("end_demand", "")))
        range_layout.addStretch()
        range_layout.addWidget(self.start_demand_field)
        range_layout.addWidget(self.end_demand_field)
        self.main_layout.addLayout(range_layout)
        self.main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        self.prob_good_demand_field, self.equal_good_checkbox = self._create_prob_section("Good Day Probs:", ' '.join(map(str, defaults.get("prob_good_demand", []))))
        self.prob_fair_demand_field, self.equal_fair_checkbox = self._create_prob_section("Fair Day Probs:", ' '.join(map(str, defaults.get("prob_fair_demand", []))))
        self.prob_poor_demand_field, self.equal_poor_checkbox = self._create_prob_section("Poor Day Probs:", ' '.join(map(str, defaults.get("prob_poor_demand", []))))

        self.main_layout.addStretch()
        self.main_layout.addLayout(self.nav_layout)
        self.add_nav_buttons(prev_callback, next_callback, prev_text="Back to Page 2", next_text="Next to Page 4")

    def _create_prob_section(self, label_text, default_text):
        layout = QVBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("color: white; font-size: 14px;")
        
        checkbox = QCheckBox("Equal Probabilities")
        checkbox.setStyleSheet("""
            QCheckBox { color: white; font-size: 12px; }
            QCheckBox::indicator { border: 1px solid #CDCDCD; border-radius: 4px; width: 13px; height: 13px; background-color: #4C4C4C; }
            QCheckBox::indicator:checked { background-color: #61AF5E; border: 1px solid #F5F5F5; }
        """)
        
        prob_field = self.make_field("e.g., 0.1 0.2 0.7", width=240, height=35)
        prob_field.setText(default_text)
        
        checkbox.toggled.connect(prob_field.setDisabled)
        
        layout.addWidget(label)
        layout.addWidget(checkbox)
        layout.addWidget(prob_field)
        self.main_layout.addLayout(layout)
        self.main_layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        
        return prob_field, checkbox

class Page4(BasePage):
    def __init__(self, prev_callback=None, next_callback=None):
        super().__init__()
        self.main_layout.addLayout(self.centered_row(self.create_title("Newspaper - Output")))
        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        self.button_group = QButtonGroup(self)
        options = ["Terminal", "Excel", "txt", "gui", "graph", "JSON", "SQLite", "Exit"]
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
        self.add_nav_buttons(prev_callback, next_callback, prev_text="Back to Page 3", next_text="Show Results")

    def get_selected_option(self):
        checked_button = self.button_group.checkedButton()
        return checked_button.text() if checked_button else None

class OutputWindow(QMainWindow):
    def __init__(self, input_params, demand_table, type_table, simulation_table, metrics):
        super().__init__()
        self.setWindowTitle("Newspaper Simulation Output")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("background-color: #4C4C4C; color: white;")

        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #888888; }
            QTabBar::tab { background: #2C2C2C; color: white; padding: 10px; border: 1px solid #888888; border-bottom: none; }
            QTabBar::tab:selected { background: #4C4C4C; border-bottom: 1px solid #4C4C4C; }
        """)
        self.setCentralWidget(tab_widget)

        tab_widget.addTab(self.create_table(metrics, is_dict=True), "Final Metrics")
        tab_widget.addTab(self.create_table(input_params, is_dict=True), "Input Parameters")
        tab_widget.addTab(self.create_table(demand_table), "Demand Distribution")
        tab_widget.addTab(self.create_table(type_table), "Day Type Distribution")
        tab_widget.addTab(self.create_table(simulation_table), "Simulation Log")

    def create_table(self, data, is_dict=False):
        if is_dict:
            table_data = list(data.items())
            table = QTableWidget(len(table_data), 2)
            table.setHorizontalHeaderLabels(["Parameter", "Value"])
            for i, (key, value) in enumerate(table_data):
                table.setItem(i, 0, QTableWidgetItem(str(key)))
                table.setItem(i, 1, QTableWidgetItem(f"{value:.2f}" if isinstance(value, float) else str(value)))
        else:
            if not data: return QTableWidget()
            table = QTableWidget(len(data), len(data[0]))
            table.setHorizontalHeaderLabels(data[0].keys())
            for i, row_data in enumerate(data):
                for j, value in enumerate(row_data.values()):
                    table.setItem(i, j, QTableWidgetItem(f"{value:.2f}" if isinstance(value, float) else str(value)))
        
        table.setStyleSheet("""
            QTableWidget { background-color: #2C2C2C; color: white; gridline-color: #888888; alternate-background-color: #3C3C3C; }
            QHeaderView::section { background-color: #61AF5E; color: black; padding: 4px; border: 1px solid #2C2C2C; }
        """)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table

class GraphOutputWindow(QMainWindow):
    def __init__(self, simulation_log):
        super().__init__()
        self.setWindowTitle("Simulation Graph - Daily Profit Over Time")
        self.setGeometry(150, 150, 900, 600)

        dark_bg = "#4C4C4C"
        light_text = "#FFFFFF"
        line_color = "#61AF5E"
        grid_color = "#888888"

        fig = Figure(figsize=(10, 6), dpi=100, facecolor=dark_bg)
        canvas = FigureCanvasQTAgg(fig)
        self.setCentralWidget(canvas)

        ax = fig.add_subplot(111)
        ax.set_facecolor(dark_bg)

        days = [row['day'] for row in simulation_log]
        profits = [row['daily_profit'] for row in simulation_log]

        ax.plot(days, profits, label='Daily Profit', color=line_color)
        ax.axhline(0, color='red', linestyle='--', linewidth=0.8, label='Break-even')

        ax.set_title('Daily Profit Over Time', color=light_text)
        ax.set_xlabel('Simulation Day', color=light_text)
        ax.set_ylabel('Profit ($)', color=light_text)

        ax.grid(True, color=grid_color, linestyle='--')
        ax.tick_params(axis='x', colors=light_text)
        ax.tick_params(axis='y', colors=light_text)

        for spine in ax.spines.values():
            spine.set_edgecolor(light_text)

        legend = ax.legend()
        legend.get_frame().set_facecolor(dark_bg)
        for text in legend.get_texts():
            text.set_color(light_text)
        
        fig.tight_layout()
