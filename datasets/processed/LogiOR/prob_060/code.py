import gurobipy as gp
from gurobipy import GRB
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import numpy as np

def solve_two_echelon_vrp():
    """
    Solves a model for the Two-Echelon Vehicle Routing Problem.
    This version correctly incorporates all constraints from the problem description,
    with comments and output in English.
    """
    console = Console()
    console.print(Panel("[bold blue]Enhanced Two-Echelon VRP Solver[/bold blue]"))

    # ========== 1. Data Preparation ==========
    # --- Define sets ---
    depot = 'D0'
    warehouses = ['W1', 'W2', 'W3']
    customers = [f'C{i}' for i in range(1, 16)]
    nodes = warehouses + customers  # All nodes for the second-echelon VRP
    
    # --- Define vehicle counts and capacities ---
    num_trucks = 3
    num_vans_per_warehouse = 2
    # Total number of vans available in the fleet
    all_vans = [f'V{i}' for i in range(1, len(warehouses) * num_vans_per_warehouse + 1)]

    truck_capacity = 50
    van_capacity = 20
    
    # --- Customer demands ---
    demands = {
        'C1':4, 'C2':7, 'C3':5, 'C4':6, 'C5':3, 'C6':8, 'C7':5, 'C8':6, 
        'C9':4, 'C10':7, 'C11':5, 'C12':6, 'C13':3, 'C14':8, 'C15':5
    }

    # --- Distance Matrix ---
    # Note: The problem provides D-W, W-W, and W-C distances, but not C-C (customer-to-customer).
    # We use a fixed random seed to generate C-C distances for reproducibility.
    dist = {}
    
    # Echelon 1: Depot to Warehouses
    dist.update({ (depot, 'W1'): 30, ('W1', depot): 30, (depot, 'W2'): 40, ('W2', depot): 40, (depot, 'W3'): 35, ('W3', depot): 35 })
    
    # Distances between warehouses (loaded for completeness, though not used in routes)
    dist.update({ ('W1', 'W2'): 25, ('W2', 'W1'): 25, ('W1', 'W3'): 20, ('W3', 'W1'): 20, ('W2', 'W3'): 30, ('W3', 'W2'): 30 })

    # Echelon 2: Warehouses to Customers
    wc_dist_data = {
        'W1': [12, 8, 15, 11, 7, 14, 10, 9, 13, 6, 14, 9, 11, 7, 13],
        'W2': [28, 22, 10, 14, 18, 9, 13, 17, 11, 20, 7, 16, 19, 12, 15],
        'W3': [18, 25, 9, 19, 24, 16, 12, 21, 7, 23, 10, 17, 22, 14, 8]
    }
    for w_idx, w in enumerate(warehouses):
        for c_idx, c in enumerate(customers):
            d = wc_dist_data[w][c_idx]
            dist[w, c] = d
            dist[c, w] = d # Distances are symmetric

    # Echelon 2: Customer to Customer (generated with a fixed seed)
    np.random.seed(42)
    for i in range(len(customers)):
        for j in range(i, len(customers)):
            c1, c2 = customers[i], customers[j]
            if i == j:
                dist[c1, c2] = 0
            else:
                d = np.random.randint(5, 25)
                dist[c1, c2] = d
                dist[c2, c1] = d

    # ========== 2. Model Creation ==========
    model = gp.Model("Fully_Constrained_2E_VRP")

    # ========== 3. Decision Variables ==========
    z = model.addVars(warehouses, vtype=GRB.BINARY, name="warehouse_open")
    y = model.addVars(customers, all_vans, vtype=GRB.BINARY, name="customer_served_by_van")
    assign_vw = model.addVars(all_vans, warehouses, vtype=GRB.BINARY, name="van_at_warehouse")
    x = model.addVars(nodes, nodes, all_vans, vtype=GRB.BINARY, name="van_route")
    
    # ========== 4. Objective Function ==========
    first_echelon_cost = gp.quicksum(2 * dist[depot, w] * z[w] for w in warehouses)
    second_echelon_cost = gp.quicksum(dist[i, j] * x[i, j, v] for i in nodes for j in nodes for v in all_vans if i != j)
    model.setObjective(first_echelon_cost + second_echelon_cost, GRB.MINIMIZE)

    # ========== 5. Constraints ==========
    # --- Assignment Constraints ---
    model.addConstrs((y.sum(c, '*') == 1 for c in customers), "C1_customer_one_van")
    model.addConstrs((assign_vw.sum(v, '*') <= 1 for v in all_vans), "C2a_van_one_warehouse")
    model.addConstrs((assign_vw[v, w] <= z[w] for v in all_vans for w in warehouses), "C2b_van_assign_to_open_wh")

    # --- Warehouse Vehicle Limit Constraint (NEW) ---
    model.addConstrs((assign_vw.sum('*', w) <= num_vans_per_warehouse for w in warehouses), "C3_warehouse_van_limit")
    
    # --- Truck Fleet Size Constraint (NEW) ---
    model.addConstr(z.sum() <= num_trucks, "C4_truck_fleet_size")
    
    # --- Capacity Constraints ---
    model.addConstrs((gp.quicksum(demands[c] * y[c, v] for c in customers) <= van_capacity for v in all_vans), "C5a_van_capacity")
    for w in warehouses:
        total_demand_at_wh = gp.quicksum(demands[c] * y[c, v] * assign_vw[v, w] for c in customers for v in all_vans)
        model.addConstr(total_demand_at_wh <= truck_capacity * z[w], f"C5b_truck_capacity_{w}")
    
    # --- Routing & Linking Constraints ---
    model.addConstrs((gp.quicksum(x[i, c, v] for i in nodes if i != c) == y[c, v] for c in customers for v in all_vans), "C6a_link_visit_in")
    model.addConstrs((gp.quicksum(x[c, j, v] for j in nodes if j != c) == y[c, v] for c in customers for v in all_vans), "C6b_link_visit_out")
    
    for v in all_vans:
        # A van must depart from its assigned warehouse
        model.addConstrs((gp.quicksum(x[w, j, v] for j in customers) <= assign_vw[v, w] for w in warehouses), f"C7a_van_departs_from_assigned_wh_{v}")
        # Each van can start at most one tour
        model.addConstr(gp.quicksum(x[w, j, v] for w in warehouses for j in customers) <= 1, f"C7b_van_departs_once_{v}")
        # The van must return to the same warehouse it departed from
        model.addConstr(gp.quicksum(x[w, j, v] for w in warehouses for j in customers) == 
                        gp.quicksum(x[i, w, v] for w in warehouses for i in customers), f"C7c_van_returns_{v}")
        
    # --- Subtour Elimination Constraints (MTZ) ---
    u = model.addVars(customers, all_vans, vtype=GRB.CONTINUOUS, name="subtour_elim_u")
    for v in all_vans:
        for i in customers:
            model.addConstr(u[i, v] <= van_capacity, f"C8a_u_upper_bound_{i}_{v}")
            model.addConstr(u[i, v] >= demands[i] * y[i, v], f"C8b_u_lower_bound_{i}_{v}")
            for j in customers:
                if i != j:
                    model.addConstr(u[i, v] - u[j, v] + van_capacity * x[i, j, v] <= van_capacity - demands[j] * y[j,v], f"C8c_subtour_elim_{i}_{j}_{v}")

    # ========== 6. Solve ==========
    model.Params.MIPGap = 0.01   # Set a 1% optimality gap tolerance
    model.optimize()

    # ========== 7. Display Results ==========
    if model.Status == GRB.OPTIMAL or (model.Status == GRB.TIME_LIMIT and model.SolCount > 0):
        status = "Optimal Solution Found" if model.Status == GRB.OPTIMAL else f"Time Limit Reached - Best Solution Found"
        console.print(Panel(f"[bold green]{status}!\nMinimized Total Distance: {model.ObjVal:.2f} km[/bold green]"))

        open_hubs = [w for w in warehouses if z[w].X > 0.5]
        console.print(f"\n[bold]Opened Warehouses:[/bold] {', '.join(open_hubs) or 'None'}")

        route_table = Table(title="[bold]Vehicle Routes and Load Details[/bold]")
        route_table.add_column("Vehicle", style="cyan", justify="center")
        route_table.add_column("Type", style="yellow", justify="center")
        route_table.add_column("Route", style="magenta", width=60)
        route_table.add_column("Load/Capacity", style="green", justify="right")
        route_table.add_column("Distance (km)", style="red", justify="right")

        for w in open_hubs:
            wh_demand = sum(demands[c] * y[c,v].X * assign_vw[v,w].X for c in customers for v in all_vans)
            route_table.add_row(f"Truck (for {w})", "Echelon 1", f"{depot} -> {w} -> {depot}", f"{wh_demand:.0f}/{truck_capacity}", f"{2*dist[depot, w]:.1f}")
        
        for v in all_vans:
            for w in warehouses:
                if assign_vw[v, w].X > 0.5:
                    tour_edges = [(i, j) for i in nodes for j in nodes if i != j and x[i, j, v].X > 0.5]
                    if not tour_edges: continue
                    
                    # Reconstruct the tour starting from the warehouse
                    tour = [w]
                    current_node = w
                    
                    while True:
                        found_next = False
                        for i, j in tour_edges:
                            if i == current_node and j not in tour:
                                tour.append(j)
                                current_node = j
                                found_next = True
                                break
                        if not found_next:
                            break # All connected edges have been added
                    
                    if tour[-1] != w: tour.append(w) # Ensure the tour is closed

                    route_str = " -> ".join(tour)
                    route_load = sum(demands.get(c, 0) for c in tour if c in customers)
                    route_dist = sum(dist.get((i, j), 0) for i, j in tour_edges)
                    route_table.add_row(v, "Echelon 2", route_str, f"{route_load}/{van_capacity}", f"{route_dist:.1f}")
        console.print(route_table)
    else:
        console.print(f"[bold red]No feasible solution found. Gurobi Status Code: {model.Status}[/bold red]")

if __name__ == "__main__":
    solve_two_echelon_vrp()
