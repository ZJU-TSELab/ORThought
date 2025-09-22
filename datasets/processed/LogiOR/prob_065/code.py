import math
import gurobipy as gp
from gurobipy import GRB
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


def solve_daily_vrp(day, required_customers, demands, vehicle_capacity,
                    num_vehicles, all_nodes, distance_matrix):
    """
    Solves a single-day Capacitated VRP for a given set of customers
    using a standard and robust flow-based formulation.
    """

    # The nodes for today's problem include the depot and only the customers that need a visit.
    daily_nodes = [0] + required_customers

    model = gp.Model(f"VRP_Day_{day}")

    # --- Decision Variables ---
    # x[i, j, v]: 1 if vehicle v travels from node i to j.
    # We create arcs only between the nodes relevant for the day.
    vehicles = list(range(1, num_vehicles + 1))
    arcs = [(i, j, v) for i in daily_nodes for j in daily_nodes
            for v in vehicles if i != j]
    x = model.addVars(arcs, vtype=GRB.BINARY, name="x")

    # --- Objective Function ---
    # Minimize the total distance traveled for the day.
    model.setObjective(
        gp.quicksum(distance_matrix[i, j] * x[i, j, v] for i, j, v in arcs),
        GRB.MINIMIZE)

    # --- Constraints ---
    # 1. Each required customer for the day is visited exactly once by some vehicle.
    model.addConstrs((gp.quicksum(x[i, c, v] for i in daily_nodes
                                  for v in vehicles if i != c) == 1
                      for c in required_customers),
                     name="visit_customer")

    # 2. Each vehicle leaves the depot at most once.
    model.addConstrs((gp.quicksum(x[0, j, v] for j in required_customers) <= 1
                      for v in vehicles),
                     name="leave_depot")

    # 3. Flow conservation: if a vehicle enters a customer node, it must leave it.
    model.addConstrs((gp.quicksum(x[i, c, v] for i in daily_nodes if i != c)
                      == gp.quicksum(x[c, j, v] for j in daily_nodes if j != c)
                      for c in required_customers for v in vehicles),
                     name="flow_conservation")

    # 4. Vehicle capacity constraint.
    model.addConstrs(
        (gp.quicksum(demands[c] * gp.quicksum(x[i, c, v]
                                              for i in daily_nodes if i != c)
                     for c in required_customers) <= vehicle_capacity
         for v in vehicles),
        name="capacity")

    # 5. Subtour Elimination (MTZ formulation).
    u = model.addVars(daily_nodes, vtype=GRB.CONTINUOUS)
    for i in required_customers:
        model.addConstr(u[i] >= demands[i])
        model.addConstr(u[i] <= vehicle_capacity)
        for j in required_customers:
            if i != j:
                model.addConstr(
                    u[i] - u[j] +
                    vehicle_capacity * gp.quicksum(x[i, j, v]
                                                   for v in vehicles)
                    <= vehicle_capacity - demands[j], f"subtour_{i}_{j}")

    # --- Solve This Day's Model ---
    model.Params.LogToConsole = 0  # Suppress solver output for daily runs
    model.optimize()

    # --- Extract and Return Results ---
    if model.Status == GRB.OPTIMAL:
        routes = []
        for v in vehicles:
            # Check if this vehicle is used by seeing if it leaves the depot
            if gp.quicksum(x[0, j, v]
                           for j in required_customers).getValue() > 0.5:
                # Reconstruct the tour for this vehicle
                tour = [0]
                current_node = 0
                while True:
                    found_next = False
                    for j in daily_nodes:
                        if j != current_node and x[current_node, j, v].X > 0.5:
                            if j == 0:  # Returned to depot
                                break
                            tour.append(j)
                            current_node = j
                            found_next = True
                            break
                    if not found_next:
                        tour.append(0)  # Final return to depot
                        break
                routes.append({'vehicle': v, 'route': tour})
        return model.ObjVal, routes
    return float('inf'), []


def solve_weekly_delivery_routing():
    """Main function to set up and solve the weekly routing problem day-by-day."""
    console = Console()
    console.print(
        Panel(
            "[bold blue]Weekly Delivery Routing Optimizer (Day-by-Day Approach)[/bold blue]"
        ))

    # ========== Problem Data ==========
    days = list(range(1, 6))
    customers = list(range(1, 16))
    vehicles = list(range(1, 4))
    depot = 0
    all_nodes = [depot] + customers
    vehicle_capacity = 200

    dist_matrix = np.array(
        [[0, 12, 18, 9, 15, 22, 7, 14, 20, 11, 16, 8, 13, 19, 10, 17],
         [12, 0, 6, 15, 21, 8, 17, 23, 10, 19, 4, 16, 5, 11, 18, 7],
         [18, 6, 0, 21, 3, 14, 9, 15, 12, 5, 10, 7, 13, 8, 4, 11],
         [9, 15, 21, 0, 18, 11, 16, 22, 7, 14, 20, 3, 19, 10, 17, 6],
         [15, 21, 3, 18, 0, 17, 12, 8, 15, 10, 7, 13, 4, 9, 14, 11],
         [22, 8, 14, 11, 17, 0, 19, 5, 12, 7, 14, 10, 17, 6, 13, 8],
         [7, 17, 9, 16, 12, 19, 0, 14, 21, 8, 15, 11, 18, 5, 12, 9],
         [14, 23, 15, 22, 8, 5, 14, 0, 17, 12, 9, 15, 6, 11, 16, 13],
         [20, 10, 12, 7, 15, 12, 21, 17, 0, 13, 18, 4, 19, 14, 9, 16],
         [11, 19, 5, 14, 10, 7, 8, 12, 13, 0, 15, 11, 6, 17, 12, 9],
         [16, 4, 10, 20, 7, 14, 15, 9, 18, 15, 0, 17, 8, 13, 18, 5],
         [8, 16, 7, 3, 13, 10, 11, 15, 4, 11, 17, 0, 14, 9, 16, 7],
         [13, 5, 13, 19, 4, 17, 18, 6, 19, 6, 8, 14, 0, 15, 10, 17],
         [19, 11, 8, 10, 9, 6, 5, 11, 14, 17, 13, 9, 15, 0, 7, 12],
         [10, 18, 4, 17, 14, 13, 12, 16, 9, 12, 18, 16, 10, 7, 0, 11],
         [17, 7, 11, 6, 11, 8, 9, 13, 16, 9, 5, 7, 17, 12, 11, 0]])
    demands = {
        c: val
        for c, val in enumerate(
            [25, 30, 20, 15, 35, 40, 18, 22, 28, 32, 19, 21, 26, 24, 23], 1)
    }

    # Define which customers to visit on each day based on frequency
    customers_by_day = {d: [] for d in days}
    frequency_map = {
        c: 1 if c <= 3 else (2 if c <= 8 else 3)
        for c in customers
    }  # Daily, Every Other, Weekly
    for c in customers:
        if frequency_map[c] == 1:  # Daily
            for d in days:
                customers_by_day[d].append(c)
        elif frequency_map[c] == 2:  # Every other day (Mon, Wed, Fri)
            customers_by_day[1].append(c)
            customers_by_day[3].append(c)
            customers_by_day[5].append(c)
        else:  # Weekly (Wednesday)
            customers_by_day[3].append(c)

    # ========== Solve and Display Results ==========
    total_weekly_distance = 0
    results_table = Table(title="Weekly Delivery Route Summary")
    results_table.add_column("Day", justify="center", style="bold yellow")
    results_table.add_column("Vehicle", justify="center", style="cyan")
    results_table.add_column("Route", justify="left", style="magenta")
    results_table.add_column("Load", justify="right")
    results_table.add_column("Distance", justify="right")

    for day in days:
        required_customers_today = customers_by_day[day]
        if not required_customers_today:
            continue

        console.print(f"\n[yellow]Optimizing routes for Day {day}...[/yellow]")
        daily_dist, daily_routes = solve_daily_vrp(day,
                                                   required_customers_today,
                                                   demands, vehicle_capacity,
                                                   len(vehicles), all_nodes,
                                                   dist_matrix)

        if daily_dist == float('inf'):
            console.print(
                f"[bold red]Could not find a feasible solution for Day {day}.[/bold red]"
            )
            continue

        total_weekly_distance += daily_dist

        for route_info in daily_routes:
            v = route_info['vehicle']
            route = route_info['route']
            route_str = " -> ".join([str(n) if n != 0 else 'D' for n in route])
            route_load = sum(demands.get(c, 0) for c in route)
            route_dist = sum(dist_matrix[route[i], route[i + 1]]
                             for i in range(len(route) - 1))
            results_table.add_row(str(day), str(v), route_str,
                                  f"{route_load}/{vehicle_capacity}",
                                  f"{route_dist:.2f}")

    console.print(results_table)
    console.print(
        Panel(
            f"[bold green]Total Weekly Distance Traveled: {total_weekly_distance:.2f} km[/bold green]"
        ))


if __name__ == "__main__":
    solve_weekly_delivery_routing()
