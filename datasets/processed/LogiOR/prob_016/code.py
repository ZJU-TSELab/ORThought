import gurobipy as gp
from gurobipy import GRB
import math

def solve_MultiDepotVRP(
    customer_num = 10,
    center_num = 2,
    customer_demand = [2, 2, 9, 1, 4, 4, 10, 6, 4, 4],
    truck_num = [3, 3],  # 3 trucks at DC 1, 3 trucks at DC 2
    truck_capacity = [20, 18],  # Capacity of trucks at DC 1 and DC 2
    customer_coord = [(-4.53, -5.12), (2.14, 5.85), (-4.88, -8.33), (2.24, 1.63),
                    (3.91, -5.88), (-1.1, 0.25), (7.92, -3.4), (-1.89, -5.0),
                    (0.72, -8.8), (-1.88, -2.89)],
    center_coord = [(-5, -5), (5, 5)]
):
    # --- Model Initialization ---
    model = gp.Model("MultiDepotVRP")
    

    # Define sets
    customers = range(1, customer_num + 1)  # Customers are 1 to 10
    dcs = range(customer_num + 1,
                customer_num + center_num + 1)  # DCs are 11 and 12
    nodes = list(customers) + list(dcs)  # All nodes

    # Create trucks for each distribution center
    all_trucks = []
    dc_to_trucks = {}
    for i, dc in enumerate(dcs):
        dc_trucks = list(range(sum(truck_num[:i]) + 1, sum(truck_num[:i + 1]) + 1))
        dc_to_trucks[dc] = dc_trucks
        all_trucks.extend(dc_trucks)

    # Create a list of all coordinates for visualization
    all_coords = {}
    for i, coord in enumerate(customer_coord):
        all_coords[i + 1] = coord  # Customer i+1 has coordinates coord
    for i, coord in enumerate(center_coord):
        all_coords[customer_num + i + 1] = coord  # DC i+1 has coordinates coord

    # Calculate distances between nodes
    distance = {}
    for i in nodes:
        for j in nodes:
            if i != j:  # No self-loops
                x1, y1 = all_coords[i]
                x2, y2 = all_coords[j]
                distance[i, j] = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    # --- Decision variables ---
    # x[i,j,k] = 1 if truck k travels from node i to node j, 0 otherwise
    x = {}
    for i in nodes:
        for j in nodes:
            if i != j:  # No self-loops
                for k in all_trucks:
                    x[i, j, k] = model.addVar(vtype=GRB.BINARY,
                                            name=f"x_{i}_{j}_{k}")

    # --- Objective function ---
    # minimize total distance traveled
    objective = gp.quicksum(distance[i, j] * x[i, j, k] for i in nodes
                            for j in nodes for k in all_trucks if i != j)
    model.setObjective(objective, GRB.MINIMIZE)

    # --- Constraints ---
    # Constraint 1: Each customer must be visited exactly once (by one truck)
    for j in customers:
        model.addConstr(gp.quicksum(x[i, j, k] for i in nodes if i != j
                                    for k in all_trucks) == 1,
                        name=f"customer_visited_{j}")

    # Constraint 2: Flow conservation - a truck that enters a customer must also leave it
    for i in customers:
        for k in all_trucks:
            model.addConstr(gp.quicksum(x[i, j, k] for j in nodes if j != i) -
                            gp.quicksum(x[j, i, k] for j in nodes if j != i) == 0,
                            name=f"flow_conservation_{i}_{k}")

    # Constraint 3: Each truck leaves its distribution center exactly once
    for d in dcs:
        for k in dc_to_trucks[d]:
            model.addConstr(gp.quicksum(x[d, j, k] for j in nodes if j != d) == 1,
                            name=f"truck_{k}_leaves_dc_{d}")

    # Constraint 4: Each truck returns to its distribution center
    for d in dcs:
        for k in dc_to_trucks[d]:
            model.addConstr(gp.quicksum(x[i, d, k] for i in customers) -
                            gp.quicksum(x[d, j, k] for j in customers) == 0,
                            name=f"truck_{k}_returns_to_dc_{d}")

    # Constraint 5: Capacity constraint for each truck
    for d_idx, d in enumerate(dcs):
        for k in dc_to_trucks[d]:
            model.addConstr(gp.quicksum(
                customer_demand[j - 1] * gp.quicksum(x[i, j, k]
                                                    for i in nodes if i != j)
                for j in customers) <= truck_capacity[d_idx],
                            name=f"truck_{k}_capacity")


    # Function to find subtours in the current solution
    def find_subtours(x_vals, k):
        """Find subtours in the current solution for truck k"""
        # Create an edge list from the solution
        edges = [(i, j) for i in nodes for j in nodes
                if i != j and (i, j, k) in x_vals and x_vals[i, j, k] > 0.5]

        if not edges:
            return []

        # Create an undirected graph for finding connected components
        neighbors = {i: [] for i in nodes}
        for i, j in edges:
            neighbors[i].append(j)

        # Find all connected components (subtours)
        unvisited = set(customers)  # Only consider customer nodes for subtours
        subtours = []

        while unvisited:
            # Start a new tour with an unvisited node
            if not unvisited:
                break
            curr = next(iter(unvisited))
            tour = [curr]
            unvisited.remove(curr)

            # Build the tour
            while neighbors[curr]:
                neighbors_of_curr = [j for j in neighbors[curr] if j in unvisited]
                if not neighbors_of_curr:
                    break

                curr = neighbors_of_curr[0]
                if curr in unvisited:  # Only add if not already in tour
                    tour.append(curr)
                    unvisited.remove(curr)

            # Check if it's a subtour (not connected to any distribution center)
            is_connected_to_dc = any(d in neighbors[node] for node in tour
                                    for d in dcs)

            if not is_connected_to_dc and len(tour) > 1:
                subtours.append(tour)

        return subtours


    # Callback function for lazy constraints
    def subtour_elimination_callback(model, where):
        if where == GRB.Callback.MIPSOL:
            # Get the current solution values
            x_vals = {}
            for i in nodes:
                for j in nodes:
                    if i != j:
                        for k in all_trucks:
                            if (i, j, k) in x:
                                val = model.cbGetSolution(x[i, j, k])
                                if val > 0.5:
                                    x_vals[i, j, k] = val

            # For each truck, find subtours and add constraints
            for k in all_trucks:
                subtours = find_subtours(x_vals, k)
                for subtour in subtours:
                    if len(subtour
                        ) >= 2:  # Only add constraints for actual subtours
                        # Add subtour elimination constraint
                        model.cbLazy(
                            gp.quicksum(x[i, j, k] for i in subtour
                                        for j in subtour
                                        if i != j) <= len(subtour) - 1)


    # Enable lazy constraints
    model._vars = x
    model.Params.lazyConstraints = 1

    # Optimize the model with the callback
    model.optimize(subtour_elimination_callback)

    # Check if the model was solved to optimality
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.objVal}
    else:
        return {"status": f"{model.status}"}

if __name__ == "__main__":
    result = solve_MultiDepotVRP()
    print(result)
