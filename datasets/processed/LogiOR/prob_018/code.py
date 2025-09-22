import gurobipy as gp
from gurobipy import GRB
import math


def solve_time_windowed_tsp(
    coordinates=[(0, 0), (-5.87, -3.3), (-4.1, 4.6), (-2.27, -7.45),
                 (4.36, 3.38), (9.05, 5.02), (-7.46, 6.97), (7.75, 7.38),
                 (0.06, -4.25), (-6.13, -9.78), (3.25, 9.86)],
    time_windows=[(8, 16), (8, 12), (9, 13), (10, 15), (11, 15), (9, 16),
                  (9, 17), (10, 18), (13, 19), (8, 16), (8, 16)],
    speed=15,
    M=10000,
    start_time=8):
    """
    Solves the Traveling Salesperson Problem with Time Windows (TSPTW).
    """
    community_num = len(coordinates) - 1
    nodes = range(community_num + 1)  # 0 is hospital, 1-10 are communities

    # Calculate distance matrix
    def calculate_distance(coord1, coord2):
        return math.sqrt(
            (coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

    distance = {}
    for i in nodes:
        for j in nodes:
            if i != j:
                distance[i, j] = calculate_distance(coordinates[i],
                                                    coordinates[j])

    # --- Model Initialization ---
    model = gp.Model("TimeWindowedTSP")

    # --- Decision variables ---
    # x[i,j] = 1 if path goes from i to j
    x = model.addVars(nodes, nodes, vtype=GRB.BINARY, name='x')
    for i in nodes:
        x[i, i].ub = 0

    # t_a[i] = arrival time at node i
    t_a = model.addVars(nodes,
                        lb=[tw[0] for tw in time_windows],
                        ub=[tw[1] for tw in time_windows],
                        vtype=GRB.CONTINUOUS,
                        name='t_a')

    # t_d[i] = departure time from node i
    t_d = model.addVars(nodes,
                        lb=[tw[0] for tw in time_windows],
                        ub=[tw[1] for tw in time_windows],
                        vtype=GRB.CONTINUOUS,
                        name='t_d')

    # Hospital departure time is fixed
    t_d[0].lb = start_time
    t_d[0].ub = start_time

    # --- Objective Function ---
    # minimize total distance
    objective = gp.quicksum(distance[i, j] * x[i, j] for i in nodes
                            for j in nodes if i != j)
    model.setObjective(objective, GRB.MINIMIZE)

    # --- Constraints ---
    # Constraint 1: Each node must be visited exactly once
    model.addConstrs((gp.quicksum(x[i, j] for i in nodes if i != j) == 1
                      for j in nodes if j != 0),
                     name='visit_to')

    # Constraint 2: Must leave each node exactly once
    model.addConstrs((gp.quicksum(x[i, j] for j in nodes if i != j) == 1
                      for i in nodes if i != 0),
                     name='leave_from')

    # Hospital constraints: must leave once and return once
    model.addConstr(gp.quicksum(x[0, j] for j in nodes if j != 0) == 1,
                    name='leave_hospital')
    model.addConstr(gp.quicksum(x[i, 0] for i in nodes if i != 0) == 1,
                    name='return_hospital')

    # Time window constraints
    for i in nodes[1:]:  # Skip hospital
        # Departure time must be after arrival time
        model.addConstr(t_d[i] >= t_a[i], name=f'depart_after_arrival_{i}')

    # Time consistency constraints
    for i in nodes:
        for j in nodes:
            if i != j:
                # If we go from i to j, arrival time at j must be after departure from i plus travel time
                model.addConstr(
                    t_d[i] + distance[i, j] / speed - M * (1 - x[i, j]) <=
                    t_a[j], f'time_consistency_min_{i}_{j}')
                model.addConstr(
                    t_d[i] + distance[i, j] / speed + M * (1 - x[i, j]) >=
                    t_a[j], f'time_consistency_max_{i}_{j}')

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
            edges = [(i, j) for i, j in x_vals.keys() if x_vals[i, j] > 0.5]

            # Find subtours
            subtours = find_subtours(edges)

            # Add subtour elimination constraints
            for S in subtours:
                if len(S) < len(nodes):
                    model.cbLazy(
                        gp.quicksum(x[i, j] for i in S for j in S
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
    result = solve_time_windowed_tsp()
    print(result)
