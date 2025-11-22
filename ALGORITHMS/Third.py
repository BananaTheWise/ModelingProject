import datetime
from datetime import datetime
import pandas as pd

from datetime import datetime
import io
import sys
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

class Algorithm:

    @staticmethod
    def prepare_simulation_inputs(
        interarrival_start,
        interarrival_end,
        interarrival_probabilities,
        num_servers,
        start_list,
        end_list,
        prob_list=None,
        num_users=20,
    ):
        """
        Return (interarrival_dist_table, interarrival_assigned_table, servers_dist_tables)

        - interarrival_start/end: either a list of interarrival times or (int start, int end)
        - interarrival_probabilities: list of probs matching interarrival times (or None -> equal)
        - start_list/end_list: per-server values. Each start_list[i] may be a list of times
          or an int paired with end_list[i] to form a range.
        - prob_list: optional list of per-server probability lists (matching service times)
        - num_users: how many users to assign random digits to (default 20)
        """
        import random
        from itertools import accumulate

        # --- build interarrival times ---
        if isinstance(interarrival_start, list):
            inter_times = list(interarrival_start)
        elif isinstance(interarrival_start, int) and isinstance(interarrival_end, int):
            inter_times = list(range(interarrival_start, interarrival_end + 1))
        else:
            raise ValueError("interarrival_start must be list or int and interarrival_end int")

        # --- probabilities for interarrival ---
        if interarrival_probabilities and len(interarrival_probabilities) == len(inter_times):
            probs = list(interarrival_probabilities)
        else:
            probs = [1.0 / len(inter_times)] * len(inter_times)

        cumul = list(accumulate(probs))
        cumul[-1] = 1.0  # enforce exact 1.0

        def rd_range_from_cum(prev_c, cur_c):
            lo = int(prev_c * 100) + 1
            hi = int(cur_c * 100)
            if lo < 1: lo = 1
            if hi > 100: hi = 100
            return f"{lo:02d} - {hi:02d}"

        interarrival_dist_table = []
        prev = 0.0
        for t, p, c in zip(inter_times, probs, cumul):
            interarrival_dist_table.append([t, round(p, 4), round(c, 4), rd_range_from_cum(prev, c)])
            prev = c

        # --- assign random digits to users (UserId, RandomDigit, InterarrivalTime) ---
        interarrival_assigned_table = []
        for i in range(num_users):
            rnd = random.randint(1, 100)
            assigned = None
            for t, p, c, rd in interarrival_dist_table:
                if rnd <= int(c * 100):
                    assigned = t
                    break
            if assigned is None:
                assigned = interarrival_dist_table[-1][0]
            interarrival_assigned_table.append((i + 1, rnd, assigned))

        # --- build servers' service-time distribution tables ---
        servers_dist_tables = []
        for s in range(num_servers):
            s_start = start_list[s]
            s_end = end_list[s] if s < len(end_list) else None

            if isinstance(s_start, list):
                service_times = list(s_start)
            elif isinstance(s_start, int) and isinstance(s_end, int):
                service_times = list(range(s_start, s_end + 1))
            else:
                raise ValueError(f"Invalid start/end for server {s+1}: {s_start}, {s_end}")

            # probs for this server
            if prob_list and s < len(prob_list) and prob_list[s] and len(prob_list[s]) == len(service_times):
                probs_for_server = list(prob_list[s])
            else:
                probs_for_server = [1.0 / len(service_times)] * len(service_times)

            cumul_s = list(accumulate(probs_for_server))
            cumul_s[-1] = 1.0
            prev_s = 0.0
            table = []
            for t_val, p_val, c_val in zip(service_times, probs_for_server, cumul_s):
                rd = rd_range_from_cum(prev_s, c_val)
                table.append([t_val, round(p_val, 4), round(c_val, 4), rd])
                prev_s = c_val

            servers_dist_tables.append(table)

        return interarrival_dist_table, interarrival_assigned_table, servers_dist_tables


    #   ===================================================================================================================================================

    #                                                   ! Service-Time Table Construction Area !

    #   ===================================================================================================================================================

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

        # If equal probabilities selected
        if probabilities is None:
            probabilities = [1 / n] * n

        # Compute cumulative probabilities
        cumulative = []
        total = 0
        for p in probabilities:
            total += p
            cumulative.append(round(total, 2))

        # Assign random-digit ranges (001â000)
        random_ranges = []
        current_start = 1  # start from 001

        for i, p in enumerate(probabilities):
            span = round(p * 100)
            if i == n - 1:
                # Last range ends at 00
                random_ranges.append(f"{current_start:02d} - 00")  # 90 09 20 04 05
            else:
                end_range = current_start + span - 1
                random_ranges.append(f"{current_start:02d} - {end_range:02d}")
                current_start = end_range + 1
                if current_start > 100:
                    current_start -= 100

        """
        | i | p   | span | range added                |
        | - | --- | ---- | -------------------------- |
        | 0 | 0.5 |  50  | `01 - 49`                |
        | 1 | 0.3 |  30  | `50 - 79`                |
        | 2 | 0.2 |  20  | `80 - 00` (wraps around) |
        """

        # start = 3 , end = 5 , n = 5 - 3 + 1 = 3 , 3 4 5
        # Combine into 2D list
        table = []
        for i in range(n):
            row = [
                times[i],  # 3 4 5
                round(probabilities[i], 2),  # span ex.300 ===> 0.3
                cumulative[i],
                random_ranges[i],  # 01-23 24-60
            ]
            table.append(row)  # [] ===> [ [data] ] ===> [ [data] , [data] ]

        # print("GID DEBUG TABLE:", table)
        """
        | i | p   | cummlative | range added                |
        | - | --- | ---------- | -------------------------- |
        | 0 | 0.5 | 0.5        | `01 - 49`                |
        | 1 | 0.3 | 0.8        | `50 - 79`                |
        | 2 | 0.2 | 1          | `80 - 00` (wraps around) |
        """

        return table

    @staticmethod
    def generate_multiple_service_distributions(num_servers, priority_list, start_list, end_list, prob_list=None):
        """
        Generate service-time distribution tables for multiple servers, ordered by priority.

        Args:
            num_servers (int): Number of servers.
            priority_list (list[int]): Priority of each server (1 = highest).
            start_list (list[int]): Start value for each server.
            end_list (list[int]): End value for each server.
            prob_list (list[list[float]] or None): List of probability lists for each server.
                                                   If None or empty, equal probabilities are used.

        Returns:
            list: List of service-time distribution tables ordered by priority.
                  Example: [ [table_for_highest_priority], [next_priority_table], ... ]
        """

        # --- Basic validation ---
        if not (len(priority_list) == len(start_list) == len(end_list) == num_servers):
            raise ValueError("All input lists must match num_servers length.")

        if prob_list is None or len(prob_list) == 0:
            prob_list = [None] * num_servers

        # --- Combine info for sorting ---
        server_info = []
        for i in range(num_servers):
            info = {
                "priority": priority_list[i],
                "start": start_list[i],
                "end": end_list[i],
                "prob": prob_list[i]
            }
            server_info.append(info)

        # --- Sort by ascending priority (1 = highest) ---
        server_info.sort(key=lambda s: s["priority"])

        # --- Generate tables ---
        all_tables = []
        for s in server_info:
            table = Algorithm.generate_service_time_distribution(
                s["start"],
                s["end"],
                s["prob"]
            )
            all_tables.append(table)

        return all_tables # all_tables[0]

    """[
        [  # priority 1 (second server)
            [3, 0.33, 0.33, '01 - 33'],
            [4, 0.33, 0.66, '34 - 66'],
            [5, 0.33, 0.99, '67 - 00']
        ],
        [  # priority 2 (third server)
            [1, 0.5, 0.5, '01 - 50'],
            [2, 0.5, 1.0, '51 - 00']
        ],
        [  # priority 3 (first server)
            [2, 0.33, 0.33, '01 - 33'],
            [3, 0.33, 0.66, '34 - 66'],
            [4, 0.33, 1.0, '67 - 00']
        ]
    ]"""

    @staticmethod
    def assign_service_times(distribution_table , random_number):
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

        service_time = None
        for time, start, end in parsed_ranges:
            if start <= random_number <= end or (end == 100 and random_number == 100):
                service_time = time
                break
            if start > end and (random_number >= start or random_number <= end):
                service_time = time
                break

        return service_time

    #   ===================================================================================================================================================

    #                                                   ! Interarrival Table Construction Area !

    #   ===================================================================================================================================================

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

        # Compute cumulative probabilities
        cumulative = []
        total = 0
        for p in probabilities:
            total += p
            cumulative.append(round(total, 3))

        # Assign random-digit ranges (001â000)
        random_ranges = []
        current_start = 1  # start from 001

        for i, p in enumerate(probabilities):
            span = round(p * 100)
            if i == n - 1:
                # Last range ends at 00
                random_ranges.append(f"{current_start:02d} - 000")  # 90 09 20 04 05
            else:
                end_range = current_start + span - 1
                random_ranges.append(f"{current_start:02d} - {end_range:02d}")
                current_start = end_range + 1
                if current_start > 100:
                    current_start -= 100

        """
        | i | p   | span | range added                |
        | - | --- | ---- | -------------------------- |
        | 0 | 0.5 | 500  | `000 - 499`                |
        | 1 | 0.3 | 300  | `500 - 799`                |
        | 2 | 0.2 | 200  | `800 - 000` (wraps around) |
        """

        # start = 3 , end = 5 , n = 5 - 3 + 1 = 3 , 3 4 5
        # Combine into 2D list
        table = []
        for i in range(n):
            row = [
                times[i],  # 3 4 5
                round(probabilities[i], 2),  # span ex.300 ===> 0.3
                cumulative[i],
                random_ranges[i],  # 01-23 24-60
            ]
            table.append(row)  # [] ===> [ [data] ] ===> [ [data] , [data] ]

        # print("GID DEBUG TABLE:", table)
        """
        | i | p   | cummlative | range added                |
        | - | --- | ---------- | -------------------------- |
        | 0 | 0.5 | 0.5        | `000 - 499`                |
        | 1 | 0.3 | 0.8        | `500 - 799`                |
        | 2 | 0.2 | 1          | `800 - 000` (wraps around) |
        """

        return table

    @staticmethod
    def generate_multiple_service_distributions(num_servers, priority_list, start_list, end_list, prob_list=None):
        """
        Generate service-time distribution tables for multiple servers, ordered by priority.

        Args:
            num_servers (int): Number of servers.
            priority_list (list[int]): Priority of each server (1 = highest).
            start_list (list[int]): Start value for each server.
            end_list (list[int]): End value for each server.
            prob_list (list[list[float]] or None): List of probability lists for each server.
                                                   If None or empty, equal probabilities are used.

        Returns:
            list[dict]: List of dictionaries containing each server's priority and its distribution table.
                        Example:
                        [
                            {"priority": 1, "table": [...]},
                            {"priority": 2, "table": [...]},
                            ...
                        ]
        """

        # --- Validation ---
        if not (len(priority_list) == len(start_list) == len(end_list) == num_servers):
            raise ValueError("All input lists must have the same length as num_servers.")

        if prob_list is None or len(prob_list) == 0:
            prob_list = [None] * num_servers
        elif len(prob_list) < num_servers:
            # Fill missing with None (equal probabilities)
            prob_list += [None] * (num_servers - len(prob_list))

        # --- Combine all server data ---
        servers_data = []
        for i in range(num_servers):
            servers_data.append({
                "priority": priority_list[i],
                "start": start_list[i],
                "end": end_list[i],
                "probabilities": prob_list[i]
            })

        # --- Sort by priority (1 = highest) ---
        servers_data.sort(key=lambda x: x["priority"])

        # --- Generate tables ---
        all_tables = []
        for server in servers_data:
            table = Algorithm.generate_service_time_distribution(
                server["start"],
                server["end"],
                server["probabilities"]
            )
            all_tables.append({
                "priority": server["priority"],
                "table": table
            })

        return all_tables

    #   ===================================================================================================================================================

    #                                                   ! Simulation Table Construction Area !

    #   ===================================================================================================================================================

    @staticmethod
    def simulate_queue(interarrival_dist_table, interarrival_assigned_table, servers_dist_tables, number_of_users=10):
        simulated_table = {
            "Users": [],
            "Interarrival Random Digit": [],
            "Interarrival Time": [],
            "Arrival Time": [],
            "Service Time Random Digit": [],
            "Servers": {},
            "Waiting Time": [],
        }

        num_servers = len(servers_dist_tables)

        # --- Initialize Servers ---
        server_status = {}  # <-- tracks each server's end_time


        for i in range(num_servers):
            servername = f"Server{i + 1}"
            simulated_table["Servers"][servername] = {
                "Start": [],
                "Service Time": [],
                "End": [],
            }
            server_status[servername] = {"end_time": 0}  # initially free

        # --- Choose Server Function ---
        def choose_server(arrival_time, servers):
            sorted_servers = sorted(servers.keys(), key=lambda n: int(n.replace("Server", "")))

            # servers free at arrival_time
            free = [name for name in sorted_servers if arrival_time >= servers[name]["end_time"]]

            if free:
                chosen = free[0]  # choose first free server
                start_time = arrival_time
            else:
                # choose the one that will be free soonest
                chosen = min(sorted_servers, key=lambda n: (servers[n]["end_time"], int(n.replace("Server", ""))))
                start_time = servers[chosen]["end_time"]

            server_num = int(chosen.replace("Server", ""))
            return server_num, start_time

        # --- Simulation Loop ---
        for i in range(number_of_users):
            user_id, rnd_digit, inter_time = interarrival_assigned_table[i]
            random_digit = random.randint(1, 100)

            simulated_table["Users"].append(user_id)
            simulated_table["Interarrival Random Digit"].append(rnd_digit)
            simulated_table["Interarrival Time"].append(inter_time)
            simulated_table["Service Time Random Digit"].append(random_digit)

            arrival_time = inter_time if i == 0 else simulated_table["Arrival Time"][i - 1] + inter_time
            simulated_table["Arrival Time"].append(arrival_time)

            # --- Assign server ---
            server_num, start_time = choose_server(arrival_time, server_status)
            server_name = f"Server{server_num}"

            service_time = Algorithm.assign_service_times(servers_dist_tables[server_num - 1], random_digit)
            end_time = start_time + service_time
            waiting_time = max(start_time - arrival_time,0)

            # --- Update server status ---
            server_status[server_name]["end_time"] = end_time

            # --- Record server times ---
            for k in range(num_servers):
                sname = f"Server{k + 1}"
                if sname == server_name:
                    simulated_table["Servers"][sname]["Start"].append(start_time)
                    simulated_table["Servers"][sname]["Service Time"].append(service_time)
                    simulated_table["Servers"][sname]["End"].append(end_time)
                else:
                    simulated_table["Servers"][sname]["Start"].append("#")
                    simulated_table["Servers"][sname]["Service Time"].append("#")
                    simulated_table["Servers"][sname]["End"].append("#")

            simulated_table["Waiting Time"].append(waiting_time)

        # --- Performance Metrics ---
        total_waiting_time = sum(simulated_table["Waiting Time"])
        total_customers = number_of_users

        avg_waiting_time = total_waiting_time / total_customers

        num_waiting_customers = sum(1 for w in simulated_table["Waiting Time"] if w > 0)
        prob_wait = num_waiting_customers / total_customers

        total_service_time = sum(
            sum(t for t in simulated_table["Servers"][s]["Service Time"] if t != "#")
            for s in simulated_table["Servers"]
        )

        # End time of last customer (max of all server end times)
        all_valid_ends = []
        for s in simulated_table["Servers"]:
            valid_ends = [t for t in simulated_table["Servers"][s]["End"] if t != "#"]
            all_valid_ends.extend(valid_ends)

        end_time_last_customer = max(all_valid_ends) if all_valid_ends else 0

        # Server Utilization (Probability Server Busy)
        server_busy_prob = total_service_time / end_time_last_customer

        # Idle Time = Total time - service time
        total_idle_time = end_time_last_customer - total_service_time
        prob_idle = total_idle_time / end_time_last_customer

        avg_service_time = total_service_time / total_customers
        avg_time_in_system = avg_waiting_time + avg_service_time

        performance_summary = f"""
        --- Queue Performance Summary ---
        1. Average Waiting Time                = {avg_waiting_time:.2f}
        2. Probability of Waiting (P(wait))    = {prob_wait:.2f}
        3. Server Utilization (P(busy))        = {server_busy_prob:.2f}
        4. Probability Server Idle (P(idle))   = {prob_idle:.2f}
        5. Average Service Time                = {avg_service_time:.2f}
        6. Average Time in System              = {avg_time_in_system:.2f}
        ---------------------------------------
        """

        # --- Print Performance Summary ---
        print(performance_summary)

        return [simulated_table, interarrival_dist_table, server_status]


        return [simulated_table,interarrival_dist_table,server_status]

    # Function 1: Print table in terminal
    @staticmethod
    def print_table_terminal(table, headers=None):
        """
        Prints a neatly aligned 2D table in the terminal with optional headers.
        Automatically adjusts column widths and handles numeric values.
        """
        if not table:
            print("(Empty table)")
            return

        # Convert all cells to strings
        str_table = [[str(cell) for cell in row] for row in table]

        # Include headers if provided
        if headers:
            str_headers = [str(h) for h in headers]
            data = [str_headers] + str_table
        else:
            data = str_table

        # Compute column widths
        col_widths = [max(len(row[i]) for row in data) for i in range(len(data[0]))]

        # Helper to format a row
        def format_row(row):
            return " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row)))

        # Print header
        if headers:
            print(format_row(headers))
            print("-" * (sum(col_widths) + 3 * (len(col_widths) - 1)))

        # Print each row
        for row in table:
            print(format_row(row))

    @staticmethod
    def print_simulation_table(simulated_table):
        print("\n===== SIMULATION TABLE =====\n")

        # --- Base columns ---
        base_keys = [
            "Users",
            "Interarrival Random Digit",
            "Interarrival Time",
            "Service Time Random Digit",
            "Arrival Time",
            "Waiting Time",
        ]

        # --- Prepare server columns ---
        server_names = list(simulated_table["Servers"].keys())
        server_columns = []
        for server in server_names:
            server_columns.extend([
                f"{server} Start",
                f"{server} Service",
                f"{server} End"
            ])

        headers = base_keys + server_columns

        # --- Build rows ---
        num_rows = len(simulated_table["Users"])
        rows = []
        for i in range(num_rows):
            row = [simulated_table[key][i] for key in base_keys]

            # Add server-specific columns
            for server in server_names:
                row.extend([
                    simulated_table["Servers"][server]["Start"][i],
                    simulated_table["Servers"][server]["Service Time"][i],
                    simulated_table["Servers"][server]["End"][i],
                ])

            rows.append(row)

        # --- Print combined table ---
        Algorithm.print_table_terminal(rows, headers)

    def run_full_simulation(
        num_users,
        interarrival_start,
        interarrival_end,
        interarrival_probabilities,
        num_servers,
        priority_list,
        start_list,
        end_list,
        prob_list=None,
    ):
        """
        Runs the full queue simulation and prints all tables step by step.

        Args:
            num_users (int): number of users/customers to simulate
            interarrival_start (int): smallest interarrival time
            interarrival_end (int): largest interarrival time
            interarrival_probabilities (list[float]): probability distribution for interarrival times
            num_servers (int): number of servers
            priority_list (list[int]): priority per server (1 = highest)
            start_list (list[int]): start service time for each server
            end_list (list[int]): end service time for each server
            prob_list (list[list[float]] or None): list of probability lists per server
        """

        print("\n==============================")
        print("🎯 QUEUE SIMULATION STARTED")
        print("==============================\n")

        # --- Step 1: Generate Interarrival Distribution ---
        interarrival_table = Algorithm.generate_interarrival_distribution(
            interarrival_start, interarrival_end, interarrival_probabilities
        )

        print("\n--- INTERARRIVAL DISTRIBUTION ---")
        Algorithm.print_table_terminal(
            interarrival_table,
            headers=["Interarrival Time", "Probability", "Cumulative", "Random-Digit Assignment"],
        )

        # --- Step 2: Assign Random Digits to Users (Interarrival) ---
        import random
        interarrival_assigned_table = []
        for i in range(num_users):
            rnd_digit = random.randint(1, 100)
            inter_time = Algorithm.assign_service_times(interarrival_table, rnd_digit)
            interarrival_assigned_table.append((i + 1, rnd_digit, inter_time))

        print("\n--- INTERARRIVAL ASSIGNED TABLE ---")
        Algorithm.print_table_terminal(
            interarrival_assigned_table,
            headers=["User", "Random Digit", "Interarrival Time"],
        )

        # --- Step 3: Generate Service Time Distributions for Servers ---
        servers_distributions = Algorithm.generate_multiple_service_distributions(
            num_servers, priority_list, start_list, end_list, prob_list
        )

        print("\n--- SERVICE TIME DISTRIBUTIONS ---")
        for idx, s in enumerate(servers_distributions):
            print(f"\nPriority {s['priority']} (Server {idx + 1})")
            Algorithm.print_table_terminal(
                s["table"],
                headers=["Service Time", "Probability", "Cumulative", "Random-Digit Assignment"],
            )

        # --- Step 4: Run Simulation ---
        simulated_table, _, _ = Algorithm.simulate_queue(
            interarrival_table,
            interarrival_assigned_table,
            [s["table"] for s in servers_distributions],
            num_users,
        )

        # --- Step 5: Print Simulation Table ---
        Algorithm.print_simulation_table(simulated_table)

        print("\n✅ Simulation Completed Successfully.\n")

    from datetime import datetime
    import pandas as pd

    from datetime import datetime
    import io
    import sys

    def print_queue_report(simulation_result, interarrival_dist_table, interarrival_assigned_table,
                           servers_dist_tables):
        simulated_table, _, server_status = simulation_result
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create a text buffer to capture all printed output
        output_buffer = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = output_buffer  # Redirect print() to buffer

        try:
            print("QUEUE SIMULATION REPORT")
            print(f"Generated on: {timestamp}")
            print("=" * 90)
            print("=" * 30)
            print("🎯 QUEUE SIMULATION STARTED")
            print("=" * 30)
            print()

            # --- Interarrival Distribution ---
            print("\n--- INTERARRIVAL DISTRIBUTION ---")
            print("Interarrival Time | Probability | Cumulative | Random-Digit Assignment")
            print("-" * 70)
            for row in interarrival_dist_table:
                print(f"{str(row[0]):<17}| {str(row[1]):<12}| {str(row[2]):<11}| {str(row[3]):<23}")

            # --- Interarrival Assigned ---
            print("\n--- INTERARRIVAL ASSIGNED TABLE ---")
            print("User | Random Digit | Interarrival Time")
            print("-" * 40)
            for row in interarrival_assigned_table:
                print(f"{str(row[0]):<5}| {str(row[1]):<13}| {str(row[2]):<18}")

            # --- Service Time Distributions ---
            print("\n--- SERVICE TIME DISTRIBUTIONS ---\n")
            for i, table in enumerate(servers_dist_tables):
                print(f"Priority Server {i + 1} (Server {i + 1})")
                print("Service Time | Probability | Cumulative | Random-Digit Assignment")
                print("-" * 65)
                for row in table:
                    print(f"{str(row[0]):<13}| {str(row[1]):<12}| {str(row[2]):<11}| {str(row[3]):<23}")
                print()

            # --- Simulation Table ---
            print("\nSimulation Table:\n")

            headers = [
                "User", "Interarrival RD", "Interarrival Time",
                "Service RD", "Arrival Time", "Waiting Time",
                "Server1 Start", "Server1 Service", "Server1 End",
                "Server2 Start", "Server2 Service", "Server2 End"
            ]

            rows = simulation_result
            col_widths = [len(h) for h in headers]
            for row in rows:
                for i, val in enumerate(row):
                    col_widths[i] = max(col_widths[i], len(str(val)))

            header_line = " | ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers))
            print(header_line)
            print("-" * len(header_line))

            for row in rows:
                print(" | ".join(f"{str(val):<{col_widths[i]}}" for i, val in enumerate(row)))

            print("\n--- End of Simulation Report ---\n")
            print("-" * 200)

            for i in range(len(simulated_table["Users"])):
                row = [
                    simulated_table["Users"][i],
                    simulated_table["Interarrival Random Digit"][i],
                    simulated_table["Interarrival Time"][i],
                    simulated_table["Service Time Random Digit"][i],
                    simulated_table["Arrival Time"][i],
                    simulated_table["Waiting Time"][i],
                ]
                for sname in simulated_table["Servers"].keys():
                    row.extend([
                        simulated_table["Servers"][sname]["Start"][i],
                        simulated_table["Servers"][sname]["Service Time"][i],
                        simulated_table["Servers"][sname]["End"][i],
                    ])
                print(" | ".join(str(x).ljust(10) for x in row))

            print("\n✅ Simulation Completed Successfully.\n")

            # --- PERFORMANCE SUMMARY ---
            print("PERFORMANCE SUMMARY")
            print("=" * 90)
            print("--- Queue Performance Summary ---")

            waiting_times = simulated_table.get("Waiting Time", [])
            if waiting_times:
                avg_wait = sum(waiting_times) / len(waiting_times)
                prob_wait = sum(1 for w in waiting_times if w > 0) / len(waiting_times)
            else:
                avg_wait = prob_wait = 0

            total_service = 0
            total_busy = 0
            total_end = 0
            total_served = 0
            all_valid_ends = []  # 🧩 collect all numeric end times across servers

            for sname, sdata in simulated_table["Servers"].items():
                service_times = [x for x in sdata["Service Time"] if isinstance(x, (int, float))]
                total_service += sum(service_times)
                total_served += len(service_times)
                total_busy += sum(service_times)

                # collect valid end times
                valid_ends = [e for e in sdata["End"] if isinstance(e, (int, float))]
                all_valid_ends.extend(valid_ends)

            # 🩵 FIXED: only compute total_end if any valid end times exist
            total_end = max(all_valid_ends) if all_valid_ends else 0

            avg_service = total_service / total_served if total_served else 0
            utilization = total_busy / (total_end * len(simulated_table["Servers"])) if total_end else 0
            idle_prob = 1 - utilization if utilization <= 1 else 0
            avg_system = avg_wait + avg_service

            print(f"1. Average Waiting Time                = {avg_wait:.2f}")
            print(f"2. Probability of Waiting (P(wait))    = {prob_wait:.2f}")
            print(f"3. Server Utilization (P(busy))        = {utilization:.2f}")
            print(f"4. Probability Server Idle (P(idle))   = {idle_prob:.2f}")
            print(f"5. Average Service Time                = {avg_service:.2f}")
            print(f"6. Average Time in System              = {avg_system:.2f}")
            print("---------------------------------------")
            print("\nEnd of Report")

        finally:
            # Restore stdout
            sys.stdout = sys_stdout

        # Write everything to file
        report_text = output_buffer.getvalue()
        with open("queue_report.txt", "w", encoding="utf-8") as f:
            f.write(report_text)

        # Optionally, print confirmation
        print("\n📝 Report saved to 'queue_report.txt'")

    @staticmethod
    def save_queue_report_to_txt(simulation_result, interarrival_dist_table,
                                 interarrival_assigned_table, servers_dist_tables,
                                 filename=None):
        """
        Same as print_queue_report(), but saves everything to a .txt file instead of printing.
        """
        from datetime import datetime
        import os

        simulated_table, _, server_status = simulation_result
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if not filename:
            filename = f"Queue_Report_{timestamp}.txt"

        lines = []
        lines.append("QUEUE SIMULATION REPORT")
        lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 90)
        lines.append("=" * 30)
        lines.append("🎯 QUEUE SIMULATION STARTED")
        lines.append("=" * 30)
        lines.append("")

        # --- Interarrival Distribution ---
        lines.append("\n--- INTERARRIVAL DISTRIBUTION ---")
        lines.append("Interarrival Time | Probability | Cumulative | Random-Digit Assignment")
        lines.append("-" * 70)
        for row in interarrival_dist_table:
            lines.append(f"{str(row[0]):<17}| {str(row[1]):<12}| {str(row[2]):<11}| {str(row[3]):<23}")

        # --- Interarrival Assigned ---
        lines.append("\n--- INTERARRIVAL ASSIGNED TABLE ---")
        lines.append("User | Random Digit | Interarrival Time")
        lines.append("-" * 40)
        for row in interarrival_assigned_table:
            lines.append(f"{str(row[0]):<5}| {str(row[1]):<13}| {str(row[2]):<18}")

        # --- Service Time Distributions ---
        lines.append("\n--- SERVICE TIME DISTRIBUTIONS ---\n")
        for i, table in enumerate(servers_dist_tables):
            lines.append(f"Priority Server {i + 1} (Server {i + 1})")
            lines.append("Service Time | Probability | Cumulative | Random-Digit Assignment")
            lines.append("-" * 65)
            for row in table:
                lines.append(f"{str(row[0]):<13}| {str(row[1]):<12}| {str(row[2]):<11}| {str(row[3]):<23}")
            lines.append("")

        # --- Simulation Table ---
        lines.append("===== SIMULATION TABLE =====\n")
        header = ["Users", "Interarrival Random Digit", "Interarrival Time",
                  "Service Time Random Digit", "Arrival Time", "Waiting Time"]
        for sname in simulated_table["Servers"].keys():
            header.extend([f"{sname} Start", f"{sname} Service", f"{sname} End"])

        lines.append(" | ".join(header))
        lines.append("-" * 200)

        for i in range(len(simulated_table["Users"])):
            row = [
                simulated_table["Users"][i],
                simulated_table["Interarrival Random Digit"][i],
                simulated_table["Interarrival Time"][i],
                simulated_table["Service Time Random Digit"][i],
                simulated_table["Arrival Time"][i],
                simulated_table["Waiting Time"][i],
            ]
            for sname in simulated_table["Servers"].keys():
                row.extend([
                    simulated_table["Servers"][sname]["Start"][i],
                    simulated_table["Servers"][sname]["Service Time"][i],
                    simulated_table["Servers"][sname]["End"][i],
                ])
            lines.append(" | ".join(str(x).ljust(10) for x in row))

        # --- PERFORMANCE SUMMARY ---
        lines.append("\n✅ Simulation Completed Successfully.\n")
        lines.append("PERFORMANCE SUMMARY")
        lines.append("=" * 90)
        lines.append("--- Queue Performance Summary ---")

        waiting_times = simulated_table["Waiting Time"]
        avg_wait = sum(waiting_times) / len(waiting_times)
        prob_wait = sum(1 for w in waiting_times if w > 0) / len(waiting_times)

        total_service = total_busy = total_end = total_served = 0
        for sname in simulated_table["Servers"].keys():
            service_times = [x for x in simulated_table["Servers"][sname]["Service Time"] if x != "#"]
            total_service += sum(service_times)
            total_served += len(service_times)
            total_busy += sum(service_times)
            total_end = max(total_end,
                            max([e for e in simulated_table["Servers"][sname]["End"] if e != "#"], default=0))

        avg_service = total_service / total_served if total_served else 0
        utilization = total_busy / (total_end * len(simulated_table["Servers"])) if total_end else 0
        idle_prob = 1 - utilization
        avg_system = avg_wait + avg_service

        lines.append(f"1. Average Waiting Time                = {avg_wait:.2f}")
        lines.append(f"2. Probability of Waiting (P(wait))    = {prob_wait:.2f}")
        lines.append(f"3. Server Utilization (P(busy))        = {utilization:.2f}")
        lines.append(f"4. Probability Server Idle (P(idle))   = {idle_prob:.2f}")
        lines.append(f"5. Average Service Time                = {avg_service:.2f}")
        lines.append(f"6. Average Time in System              = {avg_system:.2f}")
        lines.append("---------------------------------------")
        lines.append("\nEnd of Report")

        # --- Write to file ---
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"\n✅ Queue report saved to: {os.path.abspath(filename)}\n")


