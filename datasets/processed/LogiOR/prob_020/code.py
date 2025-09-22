import gurobipy as gp
from gurobipy import GRB
import math


def solve_PickupDeliveryVRP(
    order_num=10,
    truck_num=3,
    speed=30,
    maxload=1000,
    M=1e5,
    coordinates = [(0, 0), (1.41, 2.64), (6.34, -4.45), (3.04, 7.82),
                (8.18, -6.27), (3.03, 2.34), (0.07, 9.32), (0.57, -1.09),
                (8.87, 2.71), (-3.97, -3.81), (-0.08, -8.95), (8.56, 1.11),
                (3.63, -7.65), (-8.88, 9.6), (-4.31, -5.73), (7.93, 5.0),
                (-7.54, -3.57), (-5.15, -4.55), (-9.87, 0.49), (-3.91, -2.12),
                (-6.29, -7.8)],
    demands = [
        0, 198, 252, 94, 223, 163, 247, 133, 188, 216, 225, -198, -252, -94, -223,
        -163, -247, -133, -188, -216, -225
    ],
    time_windows = [(0, 1440), (570, 600), (720, 750), (630, 660), (720, 750),
                    (750, 780), (510, 540), (480, 510), (840, 870), (600, 630),
                    (570, 600), (580, 640), (730, 760), (650, 680), (720, 750),
                    (780, 810), (540, 570), (490, 520), (870, 900), (630, 660),
                    (580, 610)]
):
    # --- Model Initialization ---
    model = gp.Model("PickupDeliveryVRP")

    # Define sets
    nodes = range(order_num * 2 + 1)  # 0 is depot, 1-10 are pickup, 11-20 are delivery
    pickup_nodes = range(1, order_num + 1)
    trucks = range(truck_num)

    # Calculate distance matrix
    def calculate_distance(coord1, coord2):
        return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)


    distance = {}
    for i in nodes:
        for j in nodes:
            if i != j:
                distance[i, j] = calculate_distance(coordinates[i], coordinates[j])

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
    t_a = {}
    for i in nodes:
        t_a[i] = model.addVar(lb=time_windows[i][0],
                            ub=time_windows[i][1],
                            name=f't_a_{i}')

    # t_d[i] = departure time from node i
    t_d = {}
    for i in nodes:
        t_d[i] = model.addVar(lb=time_windows[i][0],
                            ub=time_windows[i][1],
                            name=f't_d_{i}')

    # load[i,k] = load of truck k when departing from node i
    load = {}
    for i in nodes:
        for k in trucks:
            load[i, k] = model.addVar(lb=0, ub=maxload, name=f'load_{i}_{k}')

    # --- Objective function ---
    # minimize total distance
    objective = gp.quicksum(distance[i, j] * x[i, j, k] for i in nodes
                            for j in nodes for k in trucks if i != j)
    model.setObjective(objective, GRB.MINIMIZE)

    # --- Constraints ---
    # Constraint 1: Each pickup & delivery point must be visited exactly once by one truck
    for j in nodes:
        if j != 0:  # Skip depot
            model.addConstr(gp.quicksum(x[i, j, k] for i in nodes for k in trucks
                                        if i != j) == 1,
                            name=f'visit_to_{j}')

    # Constraint 2: One order's pickup and delivery points must be visited by the same truck
    for i in pickup_nodes:
        for k in trucks:
            model.addConstr(gp.quicksum(x[i, j, k] for j in nodes
                                        if j != i) == gp.quicksum(
                                            x[i + order_num, j, k] for j in nodes
                                            if j != i + order_num),
                            name=f'same_truck_{i}_{k}')

    # Constraint 3: Flow conservation for each point
    for i in nodes:
        for k in trucks:
            model.addConstr(gp.quicksum(x[i, j, k] for j in nodes
                                        if j != i) == gp.quicksum(x[j, i, k]
                                                                for j in nodes
                                                                if j != i),
                            name=f'flow_cons_{i}_{k}')

    # Constraint 4: Each truck must leave the depot once
    for k in trucks:
        model.addConstr(gp.quicksum(x[0, j, k] for j in nodes if j != 0) == 1,
                        name=f'truck_{k}_leaves_depot')

    # Constraint 5: The order's pickup point must be visited before its delivery point
    for i in pickup_nodes:
        model.addConstr(t_a[i] <= t_d[i + order_num],
                        name=f'pickup_before_delivery_{i}')

    # Constraints 6 & 7: Time window constraints (already handled by variable bounds)

    # Constraint 8: Time consistency constraints
    for i in nodes:
        for j in nodes:
            if i != j:
                for k in trucks:
                    # If truck k goes from i to j, arrival time at j must be after departure from i plus travel time
                    model.addConstr(t_d[i] + 60 * distance[i, j] / speed - M *
                                    (1 - x[i, j, k]) <= t_a[j],
                                    name=f'time_cons_{i}_{j}_{k}')

    # Constraint 9: The truck's load must not exceed its maximum load (handled by variable bounds)

    # Constraint 10: The truck's load must be updated at every visited point
    for i in nodes:
        for j in nodes:
            if i != j:
                for k in trucks:
                    model.addConstr(load[j, k] >= load[i, k] + demands[j] - M *
                                    (1 - x[i, j, k]),
                                    name=f'load_update_lb_{i}_{j}_{k}')
                    model.addConstr(load[j, k] <= load[i, k] + demands[j] + M *
                                    (1 - x[i, j, k]),
                                    name=f'load_update_ub_{i}_{j}_{k}')

    # Constraint 11: The truck's load must be initialized at the depot
    for k in trucks:
        model.addConstr(load[0, k] == 0, name=f'initial_load_{k}')


    # Constraint 12: Eliminate sub-tours (using lazy constraints approach)
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
            for k in trucks:
                edges = [
                    (i, j) for i in nodes for j in nodes
                    if i != j and (i, j, k) in x_vals and x_vals[i, j, k] > 0.5
                ]

                subtours = find_subtours(edges)

                # Add subtour elimination constraints
                for S in subtours:
                    if len(S) < len(
                            nodes
                    ) and 0 not in S:  # Exclude depot from subtour check
                        model.cbLazy(
                            gp.quicksum(x[i, j, k] for i in S for j in S
                                        if i != j) <= len(S) - 1)


    # Enable lazy constraints
    model._vars = x
    model.Params.lazyConstraints = 1

    # Set a time limit (optional)
    model.Params.timeLimit = 3600  # 1 hour

    # Optimize model with callback
    model.optimize(subtour_cb)

    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.objVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_PickupDeliveryVRP()
    print(result)