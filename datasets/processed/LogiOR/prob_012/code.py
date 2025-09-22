import gurobipy as gp
from gurobipy import GRB
import math


def solve_vehicle_routing(
    customer_num=20,
    truck_num=5,
    truck_capacity=25,
    node_coordinates = [
        (5, 5),  # Warehouse (0)
        (5.2, 3.8),
        (8.7, 4.0),
        (7.9, 8.8),
        (1.6, 4.1),
        (8.3, 2.4),
        (4.5, 3.3),
        (3.7, 6.2),
        (8.9, 5.5),
        (8.4, 0.3),
        (0.7, 8.9),
        (0.3, 7.8),
        (5.5, 5.7),
        (2.4, 1.8),
        (3.5, 6.9),
        (5.4, 7.8),
        (2.8, 4.0),
        (4.9, 1.1),
        (6.8, 4.3),
        (9.2, 4.3),
        (0.1, 8.6)
    ],
    customer_demand = [6, 2, 7, 3, 4, 8, 7, 7, 1, 4, 1, 3, 5, 1, 2, 2, 6, 8, 2, 7],
    
):
    # --- Model Initialization ---
    model = gp.Model("VehicleRoutingProblem")
    
    # --- Define sets ---
    warehouse = 0  # Warehouse is node 0
    customers = range(1, customer_num + 1)  # Customers are 1 to 20
    nodes = [warehouse] + list(customers)  # All nodes including warehouse
    trucks = range(1, truck_num + 1)  # Trucks are 1 to 5

    # Calculate distances between nodes
    distance = {}
    for i in nodes:
        for j in nodes:
            if i != j:  # No self-loops
                x1, y1 = node_coordinates[i]
                x2, y2 = node_coordinates[j]
                distance[i, j] = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    # --- Decision Variables ---
    # x[i,j,k] = 1 if truck k travels from node i to node j, 0 otherwise
    x = {}
    for i in nodes:
        for j in nodes:
            if i != j:  # No self-loops
                for k in trucks:
                    x[i, j, k] = model.addVar(vtype=GRB.BINARY,
                                            name=f"x_{i}_{j}_{k}")
                    
    # --- Objective Function ---
    # minimize total distance traveled
    objective = gp.quicksum(distance[i, j] * x[i, j, k] for i in nodes
                            for j in nodes for k in trucks if i != j)
    model.setObjective(objective, GRB.MINIMIZE)

    # --- Constraints ---
    # Constraint 1: Each customer must be visited exactly once by exactly one truck
    for j in customers:
        model.addConstr(gp.quicksum(x[i, j, k] for i in nodes if i != j
                                    for k in trucks) == 1,
                        name=f"customer_visited_{j}")

    # Constraint 2: Flow conservation - if a truck enters a customer, it must also leave
    for i in customers:
        for k in trucks:
            model.addConstr(gp.quicksum(x[i, j, k] for j in nodes if j != i) -
                            gp.quicksum(x[j, i, k] for j in nodes if j != i) == 0,
                            name=f"flow_conservation_{i}_{k}")

    # Constraint 3: Each truck must leave the warehouse exactly once and return to it
    for k in trucks:
        model.addConstr(gp.quicksum(x[warehouse, j, k] for j in customers) == 1,
                        name=f"truck_{k}_leaves_warehouse")
        model.addConstr(gp.quicksum(x[j, warehouse, k] for j in customers) == 1,
                        name=f"truck_{k}_returns_warehouse")

    # Constraint 4: Capacity constraint for each truck
    for k in trucks:
        model.addConstr(gp.quicksum(customer_demand[j - 1] *
                                    gp.quicksum(x[i, j, k]
                                                for i in nodes if i != j)
                                    for j in customers) <= truck_capacity,
                        name=f"truck_{k}_capacity")


    # Function to find subtours in the current solution
    def find_subtours(x_vals, k):
        """Find subtours in the current solution for truck k"""
        # Create an edge list from the solution
        edges = [(i, j) for i in customers for j in customers
                if i != j and x_vals[i, j, k] > 0.5]

        if not edges:
            return []

        # Create an undirected graph for finding connected components
        neighbors = {i: [] for i in customers}
        for i, j in edges:
            neighbors[i].append(j)

        # Find all connected components (subtours)
        unvisited = set(customers)
        subtours = []

        while unvisited:
            # Start a new tour with an unvisited node
            curr = next(iter(unvisited))
            tour = [curr]
            unvisited.remove(curr)

            # Build the tour
            while True:
                neighbors_of_curr = [j for j in neighbors[curr] if j in unvisited]
                if not neighbors_of_curr:
                    break

                curr = neighbors_of_curr[0]
                tour.append(curr)
                unvisited.remove(curr)

            # Check if it's a subtour (not connected to the warehouse)
            if any(x_vals[warehouse, i, k] > 0.5
                for i in tour) and any(x_vals[i, warehouse, k] > 0.5
                                        for i in tour):
                # This is a valid tour connected to the warehouse
                continue
            elif tour:  # Only add non-empty tours
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
                        for k in trucks:
                            if (i, j, k) in x:
                                x_vals[i, j, k] = model.cbGetSolution(x[i, j, k])

            # For each truck, find subtours and add constraints
            for k in trucks:
                subtours = find_subtours(x_vals, k)
                for subtour in subtours:
                    if len(subtour) < len(
                            customers):  # Check if it's a proper subtour
                        # Add DFJ subtour elimination constraint
                        model.cbLazy(
                            gp.quicksum(x[i, j, k] for i in subtour
                                        for j in subtour
                                        if i != j) <= len(subtour) - 1)


    # Enable lazy constraints and store variables for callback
    model._vars = x
    model.Params.lazyConstraints = 1

    # --- Solve the Model ---
    model.optimize(subtour_elimination_callback)

    # --- Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}

if __name__ == "__main__":
    result = solve_vehicle_routing()
    print(result)
