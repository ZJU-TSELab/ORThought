import gurobipy as gp
from gurobipy import GRB
import math


def solve_vrptw(
    coordinates=[(0, 0), (-5, 4), (3, 6), (-2, -3), (4, -2), (-4, -5), (6, 3),
                 (-3, 5), (5, -4), (-6, -2), (2, 7), (-1, -6), (4, 5)],
    time_windows=[(6.5, 12), (7, 9), (8, 10), (7.5, 9.5), (8.5, 10.5),
                  (9, 11), (7, 9), (8, 10), (9.5, 11.5), (8, 10), (7.5, 9.5),
                  (9, 11), (8.5, 10.5)],
    demands=[0, 800, 600, 900, 700, 500, 850, 750, 600, 450, 800, 550, 700],
    unloading_times=[0, 20, 15, 25, 20, 15, 25, 20, 15, 15, 20, 15, 20],
    truck_num=5,
    speed=40,
    M=50000):
    """
    Solves the Vehicle Routing Problem with Time Windows (VRPTW).
    """
    supermarket_num = len(coordinates) - 1
    nodes = range(supermarket_num + 1)  # 0 is DC, 1-12 are supermarkets
    trucks = range(truck_num)  # 0-4 are trucks

    # Calculate distance matrix
    def calculate_distance(coord1, coord2):
        return math.sqrt((coord1[0] - coord2[0])**2 +
                         (coord1[1] - coord2[1])**2)

    distance = {}
    for i in nodes:
        for j in nodes:
            if i != j:
                distance[i, j] = calculate_distance(coordinates[i],
                                                    coordinates[j])

    # --- Model Initialization ---
    model = gp.Model("MultiVehicleTimeWindowedVRP")

    # --- Decision variables ---
    # x[i,j,k] = 1 if truck k travels from i to j
    x = {}
    for i in nodes:
        for j in nodes:
            if i != j:
                for k in trucks:
                    x[i, j, k] = model.addVar(vtype=GRB.BINARY,
                                              name=f'x_{i}_{j}_{k}')

    # t_a[i] = arrival time at node i
    t_a = model.addVars(nodes,
                        lb=[time_windows[i][0] for i in nodes],
                        ub=[time_windows[i][1] for i in nodes],
                        name='t_a')

    # t_d[i] = departure time from node i
    t_d = model.addVars(nodes,
                        lb=[time_windows[i][0] for i in nodes],
                        ub=[time_windows[i][1] for i in nodes],
                        name='t_d')

    # --- Objective function ---
    # Set objective: minimize total distance
    objective = gp.quicksum(distance[i, j] * x[i, j, k] for i in nodes
                            for j in nodes for k in trucks if i != j)
    model.setObjective(objective, GRB.MINIMIZE)

    # --- Constraints ---
    # Constraint 1: Each supermarket must be visited exactly once by one truck
    for j in nodes:
        if j != 0:  # Skip DC
            model.addConstr(
                gp.quicksum(x[i, j, k] for i in nodes for k in trucks
                            if i != j) == 1,
                name=f'visit_to_{j}')

    # Constraint 2: Each supermarket must be exited exactly once by one truck
    for i in nodes:
        if i != 0:  # Skip DC
            model.addConstr(
                gp.quicksum(x[i, j, k] for j in nodes for k in trucks
                            if i != j) == 1,
                name=f'leave_from_{i}')

    # Constraint 3: Each truck must leave the DC once
    for k in trucks:
        model.addConstr(gp.quicksum(x[0, j, k] for j in nodes if j != 0) == 1,
                        name=f'truck_{k}_leaves_dc')

    # Constraint 4: Each truck must return to the DC once
    for k in trucks:
        model.addConstr(gp.quicksum(x[i, 0, k] for i in nodes if i != 0) == 1,
                        name=f'truck_{k}_returns_dc')

    # Flow conservation for each truck at each supermarket
    for k in trucks:
        for h in nodes:
            if h != 0:  # Skip DC
                model.addConstr(
                    gp.quicksum(x[i, h, k] for i in nodes if i != h) ==
                    gp.quicksum(x[h, j, k] for j in nodes if j != h),
                    name=f'flow_cons_truck_{k}_node_{h}')

    # Time window constraints
    for i in nodes[1:]:  # Skip DC
        # Departure time must be after arrival time plus unloading time
        model.addConstr(t_d[i] >= t_a[i] + unloading_times[i] / 60,
                        name=f'depart_after_unload_{i}')

    # Time consistency constraints
    for i in nodes:
        for j in nodes:
            if i != j:
                for k in trucks:
                    # If truck k goes from i to j, arrival time at j must be after
                    # departure from i plus travel time
                    model.addConstr(
                        t_d[i] + distance[i, j] / speed - M *
                        (1 - x[i, j, k]) <= t_a[j],
                        name=f'time_cons_min_{i}_{j}_{k}')
                    model.addConstr(
                        t_d[i] + distance[i, j] / speed + M *
                        (1 - x[i, j, k]) >= t_a[j],
                        name=f'time_cons_max_{i}_{j}_{k}')

    def find_subtours(edges):
        # Create adjacency list
        adj = {i: [] for i in nodes}
        for i, j in edges:
            adj[i].append(j)

        # Find all subtours
        unvisited = set(nodes)
        subtours = []
        while unvisited:
            current = next(iter(unvisited))
            subtour = []
            while current in unvisited:
                unvisited.remove(current)
                subtour.append(current)
                next_nodes = adj.get(current, [])
                if not next_nodes:
                    break
                current = next_nodes[0]
            if len(subtour) < len(nodes):
                subtours.append(subtour)
        return subtours

    def subtour_cb(model, where):
        if where == GRB.Callback.MIPSOL:
            # Get values of binary variables
            x_vals = model.cbGetSolution(model._vars)
            edges = [(i, j, k) for i in nodes for j in nodes for k in trucks
                     if i != j and x_vals[i, j, k] > 0.5]

            # Find subtours for each truck
            for k in trucks:
                truck_edges = [(i, j) for i, j, k_idx in edges if k_idx == k]
                subtours = find_subtours(truck_edges)

                # Add subtour elimination constraints
                for S in subtours:
                    if len(S) < len(nodes) and 0 not in S:
                        model.cbLazy(
                            gp.quicksum(x[i, j, k] for i in S for j in S
                                        if i != j) <= len(S) - 1)

    # Enable lazy constraints
    model._vars = x
    model.Params.lazyConstraints = 1

    # Optimize model with callback
    model.optimize(subtour_cb)

    # --- Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_vrptw()
    print(result)
