import random

def assign_distribution_table(start, end, probabilities, value_key):
    """
    Creates a distribution table exactly like the original M,N Inventory algorithm.
    """
    table = []
    cumulative = 0
    lower = 1
    for i in range(len(probabilities)):
        p = probabilities[i]
        value = start + i
        cumulative += p
        count = int(p * 100)
        
        upper = (lower + count - 1)
        if upper >= 100:
            upper = upper % 100
        
        row = {
            value_key: value,
            "Prob": round(p, 2),
            "Cum_Prob": round(cumulative, 2),
            "Random_Digits": f"{lower:02d}-{upper:02d}"
        }
        table.append(row)
        lower = upper + 1
        if lower > 100: lower = 1

    return table

def lookup_value_from_table(rd, table, value_key):
    """
    Looks up a value from the distribution table using the original M,N Inventory logic.
    """
    for row in table:
        lower_str, upper_str = row["Random_Digits"].split('-')
        lower = int(lower_str)
        upper = 100 if upper_str == "00" else int(upper_str)

        if lower <= upper:
            if lower <= rd <= upper:
                return row[value_key]
        else:
            if rd >= lower or rd <= upper:
                return row[value_key]
    return table[-1][value_key] if table else 0


def run_inventory_simulation(inputs):
    """
    Main simulation function, with logic identical to the original M,N Inventory.
    """
    p1 = inputs["page1"]
    starting_inventory = p1["starting_inventory"]
    cycle_length = p1["cycle_length"]
    simulation_days = p1["simulation_days"]
    restock_condition = p1["restock_condition"]
    order_quantity = p1["order_quantity"]

    p2 = inputs["page2"]
    demand_probs = [float(p) for p in p2["probabilities"].split()]
    demand_table = assign_distribution_table(p2["start"], p2["end"], demand_probs, "Demand")

    p3 = inputs["page3"]
    lead_probs = [float(p) for p in p3["probabilities"].split()]
    lead_table = assign_distribution_table(p3["start"], p3["end"], lead_probs, "Lead time")

    simulation_log = []
    inventory = starting_inventory
    lead_time_remaining = None
    backorder = 0
    shortage_days = 0
    total_ending_inventory = 0
    cycle_number = 1

    for day in range(1, simulation_days + 1):
        cycle_day = (day - 1) % cycle_length + 1
        if cycle_day == 1 and day != 1:
            cycle_number += 1

        if lead_time_remaining is not None and lead_time_remaining == 0:
            if backorder > 0:
                if order_quantity >= backorder:
                    inventory += order_quantity - backorder
                    backorder = 0
                else:
                    backorder -= order_quantity
            else:
                inventory += order_quantity
            lead_time_remaining = None

        beginning_inventory = inventory

        days_until_arrival = "-"
        if lead_time_remaining is not None:
            lead_time_remaining -= 1
            days_until_arrival = lead_time_remaining

        rd_demand = random.randint(1, 100)
        demand = lookup_value_from_table(rd_demand, demand_table, "Demand")
        
        if beginning_inventory < demand:
            shortage_days += 1

        ending_inventory_calc = inventory - demand
        
        if ending_inventory_calc < 0:
            backorder += abs(ending_inventory_calc)
            ending_inventory = 0
        else:
            ending_inventory = ending_inventory_calc
            
        total_ending_inventory += ending_inventory

        order_qty_val, rd_lead_val = 0, 0
        if cycle_day == cycle_length and ending_inventory <= restock_condition:
            order_qty_val = order_quantity
            rd_lead_val = random.randint(1, 100)
            lead_days_val = lookup_value_from_table(rd_lead_val, lead_table, "Lead time")
            lead_time_remaining = lead_days_val
            days_until_arrival = lead_time_remaining

        inventory = ending_inventory
        
        cycle_display = cycle_number if cycle_day == 1 else ""

        simulation_log.append({
            "Cycle": cycle_display,
            "Day": cycle_day,
            "Begin Inv": beginning_inventory,
            "RD Demand": rd_demand,
            "Demand": demand,
            "End Inv": ending_inventory,
            "Backorder": backorder,
            "Order Qty": order_qty_val,
            "RD Lead": rd_lead_val,
            "Days Until Arrival": days_until_arrival
        })

    metrics = {
        "Total Ending Inventory": total_ending_inventory,
        "Average Ending Inventory": total_ending_inventory / simulation_days if simulation_days > 0 else 0,
        "Total Backorders": sum(row['Backorder'] for row in simulation_log),
        "Number of Orders Placed": sum(1 for row in simulation_log if row['Order Qty'] > 0),
        "Shortage Days": shortage_days,
        "Shortage Percentage": (shortage_days / simulation_days) * 100 if simulation_days > 0 else 0
    }

    final_demand_table = [{"Demand": r["Demand"], "Prob": r["Prob"], "Cum_Prob": r["Cum_Prob"], "Random_Digits": r["Random_Digits"]} for r in demand_table]
    final_lead_table = [{"Lead time": r["Lead time"], "Prob": r["Prob"], "Cum_Prob": r["Cum_Prob"], "Random_Digits": r["Random_Digits"]} for r in lead_table]

    return final_demand_table, final_lead_table, simulation_log, metrics
