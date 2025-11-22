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

    # Assign random-digit ranges
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

    # print("GID DEBUG TABLE:", table)
    return table


@staticmethod
def generate_service_time_distribution(start, end, probabilities=None):
    """
    Generate a 2D list for service-time distribution.

    Columns:
    [Service Time, Probability, Cumulative Probability, Random-Digit Assignment]

    Random-digit assignment:
      starts at 01 and wraps so the final range ends at 00 (1â100 scale).
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

    # Assign random-digit ranges (01â00)
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

    # print("GSTD Debug Table:", table)
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
            # wrap case
            if start > end and (random_digit >= start or random_digit <= end):
                interarrival_time = time
                break

        table.append([user_id, f"{random_digit:03d}", interarrival_time])

    # print("AIT Debug Table:", table)
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
            # wrap around case like
            if start > end and (random_digit >= start or random_digit <= end):
                service_time = time
                break

        table.append([cust_id, f"{random_digit:02d}", service_time])

    # print("AST Debug Table:", table)
    return table


@staticmethod
def simulate_queue(interarrival_dist, service_dist, num_users):
    inter_table = assign_interarrival_times(interarrival_dist, num_users)
    service_table = assign_service_times(service_dist, num_users)

    simulation = []
    server_available_time = 0

    for i in range(num_users):
        user = i + 1
        interarrival_time = float(inter_table[i][2])
        service_time = float(service_table[i][2])

        if i == 0:
            arrival_time = interarrival_time
        else:
            arrival_time = simulation[i - 1][2] + interarrival_time

        service_begin = max(arrival_time, server_available_time)
        waiting_time = service_begin - arrival_time
        service_end = service_begin + service_time
        time_in_system = waiting_time + service_time
        idle_time = max(0, arrival_time - server_available_time)

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

    # --- Compute Performance Metrics ---
    total_waiting = sum(row[5] for row in simulation)
    total_service = sum(row[3] for row in simulation)
    total_time_in_system = sum(row[7] for row in simulation)
    total_idle = sum(row[8] for row in simulation)

    num_waited = sum(1 for row in simulation if row[5] > 0)
    total_customers = len(simulation)

    total_simulation_time = simulation[-1][6]  # time when last service ended

    avg_waiting_time = total_waiting / total_customers
    prob_waiting = num_waited / total_customers
    avg_service_time = total_service / total_customers
    avg_time_in_system = total_time_in_system / total_customers
    server_utilization = total_service / total_simulation_time
    prob_server_idle = 1 - server_utilization

    metrics = {
        "Average Waiting Time": round(avg_waiting_time, 3),
        "Probability of Waiting": round(prob_waiting, 3),
        "Average Service Time": round(avg_service_time, 3),
        "Average Time in System": round(avg_time_in_system, 3),
        "Server Utilization": round(server_utilization, 3),
        "Probability Server Idle": round(prob_server_idle, 3)
    }

    return [simulation, metrics, inter_table, service_table]