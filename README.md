    # 0IQMachine

This is a university project for the "Modeling and Simulation" course. It's a desktop application built with PySide6 that showcases various simulation models.

## Team Members

*   Ahmed Badr 20235622
*   Hamza Sayed 20232888
*   Mohamed Sherif 20233901
*   Nour Eldin Hossam 20232773
*   Youssef Ahmed 20230172

## How to Run

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the application:**
    ```bash
    python MAIN.py
    ```

## Project Description

This project is a collection of simulation models, each demonstrating a different concept in modeling and simulation. The main application is a dashboard that provides access to each of the following simulations:

### 1. Traffic Simulation
A simulation of a 4-way intersection, designed to analyze the effects of traffic light cycles on traffic flow. The goal is to provide a decision support system for traffic engineers to test different scenarios and improve traffic control.

### 2. Single-Server Queueing System
A simulation of a single-server queueing system. Users can define the probability distributions for interarrival and service times, and the simulation will calculate various performance metrics, such as average waiting time and server utilization.

### 3. Multi-Server Queueing System
An extension of the single-server system, this simulation allows for multiple servers. Users can configure the number of servers and their individual service time distributions.

### 4. Inventory System
A simulation of an inventory system for a single product. It models daily demand and lead times for restocking, and calculates metrics such as average ending inventory and the number of stock-outs.

### 5. Event Scheduling System
A simulation of a single-server system that uses an event-scheduling approach. It processes a series of customer arrivals and departures, and provides a detailed log of events and system statistics.

### 6. Newspaper Vendor Problem
A simulation of the classic newspaper vendor problem. It models the daily profit of a vendor based on the cost of newspapers, their selling price, and the demand, which is influenced by the type of news day.

## Features

*   **Graphical User Interface:** The project features a user-friendly GUI built with PySide6, allowing for easy input of simulation parameters.
*   **Multiple Output Formats:** For each simulation, the results can be displayed in the terminal, in the GUI, or exported to various file formats, including CSV, TXT, JSON, and SQLite.
*   **Data Visualization:** Some simulations include graphical outputs to visualize the results, such as inventory levels over time.
*   **Modular Design:** The project is organized into separate modules for each simulation, making it easy to understand and extend.
