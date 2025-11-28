import random


def newspaper_simulation(buy_price, scrap_price, sell_price, num_newspapers,
                         prob_good, prob_fair, prob_poor,
                         num_days, start_demand, end_demand,
                         prob_good_demand, prob_fair_demand, prob_poor_demand):
    """
    Simple newspaper simulation function that returns output as a list

    Returns: [input_params, demand_table, type_table, simulation_table, metrics]
    """

    # Create list of demands
    demands = list(range(start_demand, end_demand + 1))

    # ============================================
    # 1. INPUT PARAMETERS
    # ============================================
    input_params = {
        'buy_price': buy_price,
        'scrap_price': scrap_price,
        'sell_price': sell_price,
        'num_newspapers': num_newspapers
    }

    # ============================================
    # 2. DEMAND TABLE
    # ============================================
    demand_table = []

    # Calculate ranges for Good, Fair, Poor
    good_cum = 0
    fair_cum = 0
    poor_cum = 0
    good_ranges = []
    fair_ranges = []
    poor_ranges = []

    for i in range(len(demands)):
        # Good day
        prev_good = good_cum
        good_cum = good_cum + prob_good_demand[i]
        start = int(prev_good * 100) + 1 if prev_good > 0 else 1
        end = int(good_cum * 100) if good_cum < 1 else 0
        good_ranges.append((start, end if end > 0 else 100))
        good_rd = f"{start:02d}-{end:02d}" if end > 0 else f"{start:02d}-00"

        # Fair day
        prev_fair = fair_cum
        fair_cum = fair_cum + prob_fair_demand[i]
        start = int(prev_fair * 100) + 1 if prev_fair > 0 else 1
        end = int(fair_cum * 100) if fair_cum < 1 else 0
        fair_ranges.append((start, end if end > 0 else 100))
        fair_rd = f"{start:02d}-{end:02d}" if end > 0 else f"{start:02d}-00"

        # Poor day
        prev_poor = poor_cum
        poor_cum = poor_cum + prob_poor_demand[i]
        start = int(prev_poor * 100) + 1 if prev_poor > 0 else 1
        end = int(poor_cum * 100) if poor_cum < 1 else 0
        poor_ranges.append((start, end if end > 0 else 100))
        poor_rd = f"{start:02d}-{end:02d}" if end > 0 else f"{start:02d}-00"

        # Add row to demand table
        demand_table.append({
            'demand': demands[i],
            'good_cumulative': good_cum,
            'good_rd': good_rd,
            'fair_cumulative': fair_cum,
            'fair_rd': fair_rd,
            'poor_cumulative': poor_cum,
            'poor_rd': poor_rd
        })

    # ============================================
    # 3. TYPE TABLE
    # ============================================
    type_table = []

    # Good
    cum_type = prob_good
    start = 1
    end = int(cum_type * 100) if cum_type < 1 else 0
    good_type_range = (start, end if end > 0 else 100)
    rd_range = f"{start:02d}-{end:02d}" if end > 0 else f"{start:02d}-00"
    type_table.append({
        'type': 'Good',
        'probability': prob_good,
        'cumulative': cum_type,
        'random_digit': rd_range
    })

    # Fair
    prev = cum_type
    cum_type = cum_type + prob_fair
    start = int(prev * 100) + 1
    end = int(cum_type * 100) if cum_type < 1 else 0
    fair_type_range = (start, end if end > 0 else 100)
    rd_range = f"{start:02d}-{end:02d}" if end > 0 else f"{start:02d}-00"
    type_table.append({
        'type': 'Fair',
        'probability': prob_fair,
        'cumulative': cum_type,
        'random_digit': rd_range
    })

    # Poor
    prev = cum_type
    cum_type = cum_type + prob_poor
    start = int(prev * 100) + 1
    end = int(cum_type * 100) if cum_type < 1 else 0
    poor_type_range = (start, end if end > 0 else 100)
    rd_range = f"{start:02d}-{end:02d}" if end > 0 else f"{start:02d}-00"
    type_table.append({
        'type': 'Poor',
        'probability': prob_poor,
        'cumulative': cum_type,
        'random_digit': rd_range
    })

    # ============================================
    # 4. SIMULATION TABLE
    # ============================================
    simulation_table = []

    total_profit = 0
    total_revenue = 0
    total_lost_profit = 0
    total_salvage = 0

    for day in range(1, num_days + 1):
        # Generate random number for type (1-100)
        rd_type = random.randint(1, 100)

        # Determine type of day
        if good_type_range[0] <= rd_type <= good_type_range[1]:
            day_type = "Good"
            demand_ranges = good_ranges
        elif fair_type_range[0] <= rd_type <= fair_type_range[1]:
            day_type = "Fair"
            demand_ranges = fair_ranges
        else:
            day_type = "Poor"
            demand_ranges = poor_ranges

        # Generate random number for demand (1-100)
        rd_demand = random.randint(1, 100)

        # Determine demand
        demand = demands[0]
        for i in range(len(demands)):
            if demand_ranges[i][0] <= rd_demand <= demand_ranges[i][1]:
                demand = demands[i]
                break

        # Calculate revenue
        papers_sold = min(demand, num_newspapers)
        revenue = papers_sold * sell_price

        # Calculate lost profit (excess demand)
        if demand > num_newspapers:
            excess_demand = demand - num_newspapers
            lost_profit = excess_demand * (sell_price - buy_price)
        else:
            lost_profit = 0

        # Calculate salvage (unsold papers)
        if num_newspapers > demand:
            unsold = num_newspapers - demand
            salvage = unsold * scrap_price
        else:
            salvage = 0

        # Calculate daily profit
        cost = buy_price * num_newspapers
        daily_profit = revenue - cost - lost_profit + salvage
        total_profit = total_profit + daily_profit
        total_revenue = total_revenue + revenue
        total_lost_profit = total_lost_profit + lost_profit
        total_salvage = total_salvage + salvage

        # Add row to simulation table
        simulation_table.append({
            'day': day,
            'rd_type': rd_type,
            'type': day_type,
            'rd_demand': rd_demand,
            'demand': demand,
            'revenue': revenue,
            'lost_profit': lost_profit,
            'salvage': salvage,
            'daily_profit': daily_profit
        })

    # ============================================
    # 5. METRICS
    # ============================================
    metrics = {
        'total_revenue': total_revenue,
        'total_lost_profit': total_lost_profit,
        'total_salvage': total_salvage,
        'total_profit': total_profit,
        'average_daily_profit': total_profit / num_days
    }

    # Return all outputs as a list
    return [input_params, demand_table, type_table, simulation_table, metrics]


# ============================================
# EXAMPLE USAGE
# ============================================
if __name__ == "__main__":
    # Run simulation
    results = newspaper_simulation(
        buy_price=0.33,
        scrap_price=0.05,
        sell_price=1.50,
        num_newspapers=10,
        prob_good=0.35,
        prob_fair=0.45,
        prob_poor=0.20,
        num_days=10,
        start_demand=8,
        end_demand=12,
        prob_good_demand=[0.03, 0.05, 0.15, 0.20, 0.57],
        prob_fair_demand=[0.10, 0.18, 0.40, 0.20, 0.12],
        prob_poor_demand=[0.44, 0.22, 0.16, 0.12, 0.06]
    )

    # Unpack results
    input_params, demand_table, type_table, simulation_table, metrics = results

    # Display results
    print("\n" + "=" * 60)
    print("INPUT PARAMETERS")
    print("=" * 60)
    print(f"1. Buy Price: ${input_params['buy_price']:.2f}")
    print(f"2. Scrap Price: ${input_params['scrap_price']:.2f}")
    print(f"3. Sell Price: ${input_params['sell_price']:.2f}")
    print(f"4. Number of daily purchased newspapers: {input_params['num_newspapers']}")

    print("\n" + "=" * 80)
    print("DEMAND TABLE")
    print("=" * 80)
    for row in demand_table:
        print(row)

    print("\n" + "=" * 60)
    print("TYPE TABLE")
    print("=" * 60)
    for row in type_table:
        print(row)

    print("\n" + "=" * 120)
    print("SIMULATION TABLE")
    print("=" * 120)
    for row in simulation_table:
        print(row)

    print("\n" + "=" * 60)
    print("METRICS")
    print("=" * 60)
    print(f"Total Revenue: ${metrics['total_revenue']:.2f}")
    print(f"Total Lost Profit: ${metrics['total_lost_profit']:.2f}")
    print(f"Total Salvage: ${metrics['total_salvage']:.2f}")
    print(f"Total Profit: ${metrics['total_profit']:.2f}")
    print(f"Average Daily Profit: ${metrics['average_daily_profit']:.2f}")
    print("=" * 60)