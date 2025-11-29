import random
from collections import deque


class EventSchedulingSimulation:
    def __init__(self, num_customers, stop_time):
        self.num_customers = num_customers
        self.stop_time = stop_time
        self.clock = 0
        self.LQ = 0
        self.LS = 0
        self.checkout_line = deque()
        self.current_customer = None
        self.FEL = []
        self.total_time_in_system = 0
        self.num_departures = 0
        self.total_busy_time = 0
        self.max_queue_length = 0
        self.event_table = []
        self.simulation_table = []
        self.customer_arrival_times = {}

    def generate_interarrival_time(self):
        return random.randint(1, 8)

    def generate_service_time(self):
        return random.randint(2, 10)

    def generate_event_table(self):
        arrival_time = 0

        for i in range(1, self.num_customers + 1):
            if i == 1:
                interarrival_time = 0
            else:
                interarrival_time = self.generate_interarrival_time()

            arrival_time += interarrival_time
            service_time = self.generate_service_time()

            self.event_table.append({
                'customer': i,
                'interarrival': interarrival_time,
                'arrival': arrival_time,
                'service': service_time,
                'departure': None
            })

            self.FEL.append(('A', i, arrival_time))

        self.FEL.sort(key=lambda x: x[2])

    def format_checkout_line(self):
        formatted = []

        if self.current_customer is not None:
            arrival_time = self.customer_arrival_times.get(self.current_customer, 0)
            formatted.append(f"(C{self.current_customer},{arrival_time})")

        for customer_num in self.checkout_line:
            arrival_time = self.customer_arrival_times.get(customer_num, 0)
            formatted.append(f"(C{customer_num},{arrival_time})")

        return ' '.join(formatted) if formatted else '-'

    def format_fel(self, current_event_type):
        formatted = []

        next_arrival = None
        for event in self.FEL:
            if event[0] == 'A':
                next_arrival = event
                break

        next_departure = None
        for event in self.FEL:
            if event[0] == 'D':
                next_departure = event
                break

        if current_event_type.startswith('A'):
            if next_arrival:
                formatted.append(f"(A{next_arrival[1]},{next_arrival[2]})")

            if next_departure:
                formatted.append(f"(D{next_departure[1]},{next_departure[2]})")

        elif current_event_type.startswith('D'):
            if next_arrival:
                formatted.append(f"(A{next_arrival[1]},{next_arrival[2]})")

            if next_departure:
                formatted.append(f"(D{next_departure[1]},{next_departure[2]})")

        formatted.append(f"(E,{self.stop_time})")

        return ' '.join(formatted)

    def add_simulation_row(self, event_type):
        checkout_str = self.format_checkout_line()
        fel_str = self.format_fel(event_type)

        self.simulation_table.append({
            'clock': self.clock,
            'event': event_type,
            'LQ': self.LQ,
            'LS': self.LS,
            'checkout': checkout_str,
            'FEL': fel_str,
            'S': self.total_time_in_system,
            'N': self.num_departures,
            'B': self.total_busy_time,
            'MQ': self.max_queue_length
        })

    def process_arrival(self, customer_num):
        event_type = f"A{customer_num}"

        self.customer_arrival_times[customer_num] = self.clock

        if self.LS == 0:
            self.LS = 1
            self.current_customer = customer_num

            service_time = next(e['service'] for e in self.event_table if e['customer'] == customer_num)
            departure_time = self.clock + service_time

            for event in self.event_table:
                if event['customer'] == customer_num:
                    event['departure'] = departure_time
                    break

            self.FEL.append(('D', customer_num, departure_time))
            self.FEL.sort(key=lambda x: x[2])
        else:
            self.checkout_line.append(customer_num)
            self.LQ += 1
            self.max_queue_length = max(self.max_queue_length, self.LQ)

        self.add_simulation_row(event_type)

    def process_departure(self, customer_num):
        event_type = f"D{customer_num}"

        arrival_time = self.customer_arrival_times[customer_num]
        time_in_system = self.clock - arrival_time
        self.total_time_in_system += time_in_system
        self.num_departures += 1

        service_time = next(e['service'] for e in self.event_table if e['customer'] == customer_num)
        self.total_busy_time += service_time

        self.current_customer = None

        if self.LQ > 0:
            next_customer = self.checkout_line.popleft()
            self.LQ -= 1

            self.current_customer = next_customer

            service_time = next(e['service'] for e in self.event_table if e['customer'] == next_customer)
            departure_time = self.clock + service_time

            for event in self.event_table:
                if event['customer'] == next_customer:
                    event['departure'] = departure_time
                    break

            self.FEL.append(('D', next_customer, departure_time))
            self.FEL.sort(key=lambda x: x[2])
        else:
            self.LS = 0

        self.add_simulation_row(event_type)

    def run_simulation(self):
        while self.FEL and self.clock < self.stop_time:
            current_time = self.FEL[0][2]
            simultaneous_events = []

            while self.FEL and self.FEL[0][2] == current_time:
                simultaneous_events.append(self.FEL.pop(0))

            self.clock = current_time

            if self.clock > self.stop_time:
                break

            arrivals = [e for e in simultaneous_events if e[0] == 'A']
            departures = [e for e in simultaneous_events if e[0] == 'D']

            if len(arrivals) > 0 and len(departures) > 0:
                for event in departures:
                    _, customer_num, _ = event
                    arrival_time = self.customer_arrival_times[customer_num]
                    time_in_system = self.clock - arrival_time
                    self.total_time_in_system += time_in_system
                    self.num_departures += 1

                    service_time = next(e['service'] for e in self.event_table if e['customer'] == customer_num)
                    self.total_busy_time += service_time
                    self.current_customer = None

                    if self.LQ > 0:
                        next_customer = self.checkout_line.popleft()
                        self.LQ -= 1
                        self.current_customer = next_customer
                        service_time = next(e['service'] for e in self.event_table if e['customer'] == next_customer)
                        departure_time = self.clock + service_time
                        for evt in self.event_table:
                            if evt['customer'] == next_customer:
                                evt['departure'] = departure_time
                                break
                        self.FEL.append(('D', next_customer, departure_time))
                        self.FEL.sort(key=lambda x: x[2])
                    else:
                        self.LS = 0

                for event in arrivals:
                    _, customer_num, _ = event
                    self.customer_arrival_times[customer_num] = self.clock

                    if self.LS == 0:
                        self.LS = 1
                        self.current_customer = customer_num
                        service_time = next(e['service'] for e in self.event_table if e['customer'] == customer_num)
                        departure_time = self.clock + service_time
                        for evt in self.event_table:
                            if evt['customer'] == customer_num:
                                evt['departure'] = departure_time
                                break
                        self.FEL.append(('D', customer_num, departure_time))
                        self.FEL.sort(key=lambda x: x[2])
                    else:
                        self.checkout_line.append(customer_num)
                        self.LQ += 1
                        self.max_queue_length = max(self.max_queue_length, self.LQ)

                event_type = f"D{departures[0][1]}/A{arrivals[0][1]}"
                self.add_simulation_row(event_type)

            else:
                for event in simultaneous_events:
                    event_type_char, customer_num, _ = event
                    if event_type_char == 'A':
                        self.process_arrival(customer_num)
                    elif event_type_char == 'D':
                        self.process_departure(customer_num)

    def get_event_table(self):
        """Returns the event table as a list of dictionaries"""
        return self.event_table.copy()

    def get_simulation_table(self):
        """Returns the simulation table as a list of dictionaries"""
        return self.simulation_table.copy()

    def get_statistics(self):
        """Returns the final statistics as a dictionary"""
        avg_time_in_system = int(self.total_time_in_system / self.num_departures) if self.num_departures > 0 else 0
        server_utilization = int((self.total_busy_time / self.clock) * 100) if self.clock > 0 else 0

        return {
            'total_simulation_time': self.clock,
            'total_customers_processed': self.num_departures,
            'total_time_in_system': self.total_time_in_system,
            'average_time_in_system': avg_time_in_system,
            'total_server_busy_time': self.total_busy_time,
            'server_utilization': server_utilization,
            'maximum_queue_length': self.max_queue_length
        }


def run_event_scheduling_simulation(num_customers, stop_time):
    """
    Run the event scheduling simulation and return results.

    Args:
        num_customers: Number of customers to simulate
        stop_time: Simulation end time

    Returns:
        A dictionary containing:
            - 'event_table': List of event records
            - 'simulation_table': List of simulation state records
            - 'statistics': Dictionary of final statistics
    """
    sim = EventSchedulingSimulation(num_customers, stop_time)
    sim.generate_event_table()
    sim.run_simulation()

    return {
        'event_table': sim.get_event_table(),
        'simulation_table': sim.get_simulation_table(),
        'statistics': sim.get_statistics()
    }


# Example usage:
if __name__ == "__main__":
    results = run_event_scheduling_simulation(num_customers=5, stop_time=50)

    print("Event Table:")
    for event in results['event_table']:
        print(event)

    print("\nSimulation Table:")
    for row in results['simulation_table']:
        print(row)

    print("\nStatistics:")
    for key, value in results['statistics'].items():
        print(f"{key}: {value}")