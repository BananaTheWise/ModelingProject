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
    QCheckBox,
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
)
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

from MAIN import DashboardWindow
from GUI.Basics import BasePage
from ALGORITHMS.Fourth import run_inventory_simulation

matplotlib.use('QtAgg')


class FourthAssignment(QMainWindow):

    def go_prev(self):
        idx = self.stacked.currentIndex()
        if idx > 0:
            self.stacked.setCurrentIndex(idx - 1)

    def go_next(self):
        idx = self.stacked.currentIndex()
        current_page = self.pages[idx]

        try:
            if isinstance(current_page, Page1):
                self.input_data["page1"]["starting_inventory"] = int(current_page.starting_inventory_field.text())
                self.input_data["page1"]["cycle_length"] = int(current_page.cycle_length_field.text())
                self.input_data["page1"]["simulation_days"] = int(current_page.simulation_days_field.text())
                self.input_data["page1"]["restock_condition"] = int(current_page.restock_condition_field.text())
                self.input_data["page1"]["order_quantity"] = int(current_page.order_quantity_field.text())

            elif isinstance(current_page, (Page2, Page3)):
                page_key = "page2" if isinstance(current_page, Page2) else "page3"
                start = int(current_page.start_field.text())
                end = int(current_page.end_field.text())
                
                if current_page.equal_checkbox.isChecked():
                    num_values = end - start + 1
                    prob = 1 / num_values
                    probs_text = " ".join([f"{prob:.4f}"] * num_values)
                else:
                    probs_text = current_page.prob_field.text().strip()
                    prob_items = [x for x in probs_text.split() if x]
                    probs = [float(x) for x in prob_items]

                    if len(prob_items) != (end - start + 1):
                        QMessageBox.warning(self, "Invalid Input", f"Number of probabilities must match the range size ({end - start + 1})")
                        return

                    if abs(sum(probs) - 1.0) > 1e-6:
                        QMessageBox.warning(self, "Invalid Input", "Sum of probabilities must equal 1")
                        return

                self.input_data[page_key]["start"] = start
                self.input_data[page_key]["end"] = end
                self.input_data[page_key]["probabilities"] = probs_text
                self.input_data[page_key]["equal"] = current_page.equal_checkbox.isChecked()

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

        demand_table, lead_table, simulation_log, metrics = run_inventory_simulation(self.input_data)

        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if selected_option == "Terminal":
            self.output_to_terminal(demand_table, lead_table, simulation_log, metrics)
        elif selected_option == "Excel":
            self.output_to_csv(demand_table, lead_table, simulation_log, metrics, output_dir)
        elif selected_option == "txt":
            self.output_to_txt(demand_table, lead_table, simulation_log, metrics, output_dir)
        elif selected_option == "gui":
            self.output_to_gui(demand_table, lead_table, simulation_log, metrics)
        elif selected_option == "graph":
            self.output_to_graph(simulation_log)
        elif selected_option == "JSON":
            self.output_to_json(demand_table, lead_table, simulation_log, metrics, output_dir)
        elif selected_option == "SQLite":
            self.output_to_sqlite(demand_table, lead_table, simulation_log, metrics, output_dir)

    def output_to_graph(self, simulation_log):
        self.graph_window = GraphOutputWindow(simulation_log)
        self.graph_window.show()

    def output_to_json(self, demand_table, lead_table, simulation_log, metrics, output_dir):
        path = os.path.join(output_dir, "inventory_simulation_output.json")
        output_data = {
            "metrics": metrics,
            "demand_distribution": demand_table,
            "lead_time_distribution": lead_table,
            "simulation_log": simulation_log
        }
        try:
            with open(path, "w") as f:
                json.dump(output_data, f, indent=4)
            QMessageBox.information(self, "Success", f"Output saved to {os.path.abspath(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not write to JSON file: {e}")

    def output_to_sqlite(self, demand_table, lead_table, simulation_log, metrics, output_dir):
        path = os.path.join(output_dir, "inventory_simulation_output.db")
        try:
            if os.path.exists(path):
                os.remove(path)
            conn = sqlite3.connect(path)
            cursor = conn.cursor()

            cursor.execute("CREATE TABLE metrics (metric TEXT, value REAL)")
            cursor.execute("CREATE TABLE demand_distribution (Demand INTEGER, Prob REAL, Cum_Prob REAL, Random_Digits TEXT)")
            cursor.execute("CREATE TABLE lead_time_distribution ('Lead time' INTEGER, Prob REAL, Cum_Prob REAL, Random_Digits TEXT)")
            log_headers = [f'"{h}"' for h in simulation_log[0].keys()]
            cursor.execute(f"CREATE TABLE simulation_log ({', '.join(log_headers)})")

            cursor.executemany("INSERT INTO metrics VALUES (?, ?)", metrics.items())
            cursor.executemany("INSERT INTO demand_distribution VALUES (?, ?, ?, ?)", [tuple(r.values()) for r in demand_table])
            cursor.executemany("INSERT INTO lead_time_distribution VALUES (?, ?, ?, ?)", [tuple(r.values()) for r in lead_table])
            cursor.executemany(f"INSERT INTO simulation_log VALUES ({', '.join(['?'] * len(log_headers))})", [tuple(r.values()) for r in simulation_log])

            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", f"Output saved to {os.path.abspath(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not write to SQLite file: {e}")


    def output_to_terminal(self, demand_table, lead_table, simulation_log, metrics):
        print("--- Demand Distribution ---")
        print(f"{'Demand':<10}{'Prob':<10}{'Cum Prob':<10}{'Range':<15}")
        for row in demand_table:
            print(f"{row['Demand']:<10}{row['Prob']:<10.2f}{row['Cum_Prob']:<10.2f}{row['Random_Digits']}")

        print("\n--- Lead Time Distribution ---")
        print(f"{'Lead Time':<10}{'Prob':<10}{'Cum Prob':<10}{'Range':<15}")
        for row in lead_table:
            print(f"{row['Lead time']:<10}{row['Prob']:<10.2f}{row['Cum_Prob']:<10.2f}{row['Random_Digits']}")

        print("\n--- Simulation Log ---")
        headers = simulation_log[0].keys()
        print(" | ".join(f"{h:<12}" for h in headers))
        for row in simulation_log:
            print(" | ".join(f"{str(v):<12}" for v in row.values()))
            
        print("\n--- Simulation Metrics ---")
        for key, value in metrics.items():
            print(f"{key}: {value:.2f}")

        QMessageBox.information(self, "Output", "Results printed to terminal.")

    def output_to_csv(self, demand_table, lead_table, simulation_log, metrics, output_dir):
        path = os.path.join(output_dir, "inventory_simulation_output.csv")
        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["--- Demand Distribution ---"])
                writer.writerow(demand_table[0].keys())
                for row in demand_table:
                    writer.writerow(row.values())

                writer.writerow([])
                writer.writerow(["--- Lead Time Distribution ---"])
                writer.writerow(lead_table[0].keys())
                for row in lead_table:
                    writer.writerow(row.values())

                writer.writerow([])
                writer.writerow(["--- Simulation Log ---"])
                writer.writerow(simulation_log[0].keys())
                for row in simulation_log:
                    writer.writerow(row.values())
                    
                writer.writerow([])
                writer.writerow(["--- Simulation Metrics ---"])
                writer.writerow(metrics.keys())
                writer.writerow(metrics.values())

            QMessageBox.information(self, "Success", f"Output saved to {os.path.abspath(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not write to CSV file: {e}")

    def output_to_txt(self, demand_table, lead_table, simulation_log, metrics, output_dir):
        path = os.path.join(output_dir, "inventory_simulation_output.txt")
        try:
            with open(path, "w") as f:
                f.write("--- Demand Distribution ---\n")
                f.write(f"{'Demand':<10}{'Prob':<10}{'Cum Prob':<10}{'Range':<15}\n")
                for row in demand_table:
                    f.write(f"{row['Demand']:<10}{row['Prob']:<10.2f}{row['Cum_Prob']:<10.2f}{row['Random_Digits']}\n")

                f.write("\n--- Lead Time Distribution ---\n")
                f.write(f"{'Lead Time':<10}{'Prob':<10}{'Cum Prob':<10}{'Range':<15}\n")
                for row in lead_table:
                    f.write(f"{row['Lead time']:<10}{row['Prob']:<10.2f}{row['Cum_Prob']:<10.2f}{row['Random_Digits']}\n")

                f.write("\n--- Simulation Log ---\n")
                headers = simulation_log[0].keys()
                f.write(" | ".join(f"{h:<12}" for h in headers) + "\n")
                for row in simulation_log:
                    f.write(" | ".join(f"{str(v):<12}" for v in row.values()) + "\n")
                    
                f.write("\n--- Simulation Metrics ---\n")
                for key, value in metrics.items():
                    f.write(f"{key}: {value:.2f}\n")

            QMessageBox.information(self, "Success", f"Output saved to {os.path.abspath(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not write to TXT file: {e}")

    def output_to_gui(self, demand_table, lead_table, simulation_log, metrics):
        self.output_window = OutputWindow(demand_table, lead_table, simulation_log, metrics)
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
        self.setWindowTitle("Inventory Simulation")
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
            "page1": {"starting_inventory": 25, "cycle_length": 7, "simulation_days": 365, "restock_condition": 15, "order_quantity": 50},
            "page2": {"start": 3, "end": 8, "probabilities": "0.10 0.20 0.30 0.20 0.15 0.05", "equal": False},
            "page3": {"start": 1, "end": 3, "probabilities": "0.30 0.50 0.20", "equal": False},
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

        title_btn = QPushButton("Inventory - Inputs")
        title_btn.setEnabled(False)
        title_btn.setFixedSize(167, 30)
        title_btn.setStyleSheet("background-color: #CDCDCD; border: 2px solid #BBBBBB; border-radius: 12px; font-size: 17px; color: #2C2C2C;")
        self.main_layout.addLayout(self.centered_row(title_btn))
        self.main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        self.starting_inventory_field = self._create_input_row(form_layout, "Starting Inventory:", "(ex. 25)", str(defaults.get("starting_inventory", "")))
        self.order_quantity_field = self._create_input_row(form_layout, "Order Quantity:", "(ex. 50)", str(defaults.get("order_quantity", "")))
        self.cycle_length_field = self._create_input_row(form_layout, "Cycle Length:", "(ex. 7)", str(defaults.get("cycle_length", "")))
        self.simulation_days_field = self._create_input_row(form_layout, "Simulation Days:", "(ex. 365)", str(defaults.get("simulation_days", "")))
        self.restock_condition_field = self._create_input_row(form_layout, "Condition for Restock:", "(ex. 15)", str(defaults.get("restock_condition", "")))

        self.main_layout.addLayout(form_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.nav_layout)
        self.add_nav_buttons(prev_callback, next_callback, prev_text="Back to Main", next_text="Next to Page 2")

    def _create_input_row(self, layout, label_text, example_text, default_value):
        row = QHBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("color: white; font-size: 14px;")
        field = self.make_field("")
        field.setText(default_value)
        field.setValidator(QIntValidator(0, 1000000))
        example_label = QLabel(example_text)
        example_label.setStyleSheet("color: gray; font-size: 12px;")

        row.addWidget(label)
        row.addStretch()
        row.addWidget(field)
        layout.addLayout(row)
        example_row = QHBoxLayout()
        example_row.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        example_row.addWidget(example_label)
        layout.addLayout(example_row)
        return field


class DistributionPage(BasePage):
    def __init__(self, title, prev_callback=None, next_callback=None, defaults=None, nav_texts=None):
        super().__init__()
        defaults = defaults or {}
        nav_texts = nav_texts or {}

        title_btn = QPushButton(title)
        title_btn.setEnabled(False)
        title_btn.setFixedSize(180, 30)
        title_btn.setStyleSheet("background-color: #CDCDCD; border: 2px solid #BBBBBB; border-radius: 12px; font-size: 17px; color: #2C2C2C;")
        self.main_layout.addLayout(self.centered_row(title_btn))
        self.main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        range_label = QLabel("Range")
        range_label.setStyleSheet("color: white; font-size: 14px;")
        self.start_field = self.make_field("Start")
        self.start_field.setText(str(defaults.get("start", "")))
        self.start_field.setValidator(QIntValidator(0, 10000))
        self.end_field = self.make_field("End")
        self.end_field.setText(str(defaults.get("end", "")))
        self.end_field.setValidator(QIntValidator(0, 10000))
        range_row = QHBoxLayout()
        range_row.addWidget(range_label)
        range_row.addStretch()
        range_row.addWidget(self.start_field)
        range_row.addWidget(self.end_field)
        self.main_layout.addLayout(range_row)
        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        self.equal_checkbox = QCheckBox("Equal")
        self.equal_checkbox.setStyleSheet("""
            QCheckBox { color: white; font-size: 14px; }
            QCheckBox::indicator {
                border: 2px solid #CDCDCD;
                border-radius: 4px;
                width: 15px;
                height: 15px;
                background-color: #4C4C4C;
            }
            QCheckBox::indicator:checked {
                background-color: #61AF5E;
                border: 2px solid #F5F5F5;
            }
        """)
        equal_text = QLabel("All probabilities are the same")
        equal_text.setStyleSheet("color: gray; font-size: 12px;")
        self.equal_checkbox.setChecked(defaults.get("equal", False))
        self.main_layout.addWidget(self.equal_checkbox)
        self.main_layout.addWidget(equal_text)
        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        prob_label = QLabel("Probabilities")
        prob_label.setStyleSheet("color: white; font-size: 14px;")
        self.prob_field = self.make_field("Sum of Probs. must equal 1", width=200, height=40)
        self.prob_field.setText(defaults.get("probabilities", ""))
        regex = QRegularExpression(r"^(\d*\.?\d+\s*)+$")
        validator = QRegularExpressionValidator(regex)
        self.prob_field.setValidator(validator)
        self.main_layout.addWidget(prob_label)
        self.main_layout.addWidget(self.prob_field)
        
        self.equal_checkbox.toggled.connect(self.prob_field.setDisabled)
        self.prob_field.setDisabled(self.equal_checkbox.isChecked())


        self.main_layout.addStretch()
        self.main_layout.addLayout(self.nav_layout)
        self.add_nav_buttons(prev_callback, next_callback, **nav_texts)


class Page2(DistributionPage):
    def __init__(self, prev_callback=None, next_callback=None, defaults=None):
        nav_texts = {"prev_text": "Back to Page 1", "next_text": "Next to Page 3"}
        super().__init__("Inventory - Demand", prev_callback, next_callback, defaults, nav_texts)


class Page3(DistributionPage):
    def __init__(self, prev_callback=None, next_callback=None, defaults=None):
        nav_texts = {"prev_text": "Back to Page 2", "next_text": "Next to Page 4"}
        super().__init__("Inventory - Lead Time", prev_callback, next_callback, defaults, nav_texts)


class Page4(BasePage):
    def __init__(self, prev_callback=None, next_callback=None):
        super().__init__()
        title_btn = QPushButton("Inventory - Output")
        title_btn.setEnabled(False)
        title_btn.setFixedSize(180, 30)
        title_btn.setStyleSheet("background-color: #CDCDCD; border: 2px solid #BBBBBB; border-radius: 12px; font-size: 17px; color: #2C2C2C;")
        self.main_layout.addLayout(self.centered_row(title_btn))
        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        self.button_group = QButtonGroup(self)
        options = ["Terminal", "Excel", "txt", "gui", "graph", "JSON", "SQLite", "Exit"]
        for option in options:
            radio_button = QRadioButton(option)
            radio_button.setStyleSheet("""
                QRadioButton { color: white; font-size: 14px; }
                QRadioButton::indicator {
                    border: 2px solid #CDCDCD;
                    border-radius: 9px;
                    width: 15px;
                    height: 15px;
                    background-color: #4C4C4C;
                }
                QRadioButton::indicator:checked {
                    background-color: #61AF5E;
                    border: 2px solid #F5F5F5;
                }
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
    def __init__(self, demand_table, lead_table, simulation_log, metrics):
        super().__init__()
        self.setWindowTitle("Simulation Output")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        layout.addWidget(QLabel("Simulation Metrics"))
        metrics_table_widget = self.create_metrics_table(metrics)
        layout.addWidget(metrics_table_widget)

        layout.addWidget(QLabel("Demand Distribution"))
        demand_table_widget = self.create_table(demand_table)
        layout.addWidget(demand_table_widget)

        layout.addWidget(QLabel("Lead Time Distribution"))
        lead_table_widget = self.create_table(lead_table)
        layout.addWidget(lead_table_widget)

        layout.addWidget(QLabel("Simulation Log"))
        sim_table_widget = self.create_table(simulation_log)
        layout.addWidget(sim_table_widget)

    def create_table(self, data):
        if not data:
            return QTableWidget()
        
        table = QTableWidget(len(data), len(data[0]))
        table.setHorizontalHeaderLabels(data[0].keys())
        
        for i, row_data in enumerate(data):
            for j, (key, value) in enumerate(row_data.items()):
                table.setItem(i, j, QTableWidgetItem(str(value)))
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table

    def create_metrics_table(self, data):
        table = QTableWidget(len(data), 2)
        table.setHorizontalHeaderLabels(["Metric", "Value"])
        
        for i, (key, value) in enumerate(data.items()):
            table.setItem(i, 0, QTableWidgetItem(key))
            table.setItem(i, 1, QTableWidgetItem(f"{value:.2f}"))
            
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table

class GraphOutputWindow(QMainWindow):
    def __init__(self, simulation_log):
        super().__init__()
        self.setWindowTitle("Simulation Graph - Inventory Over Time")
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
        inventory_levels = [row['end_inv'] for row in simulation_log]

        ax.plot(days, inventory_levels, label='Ending Inventory', color=line_color)

        ax.set_title('Inventory Level Over Time', color=light_text)
        ax.set_xlabel('Simulation Day', color=light_text)
        ax.set_ylabel('Units in Inventory', color=light_text)

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
