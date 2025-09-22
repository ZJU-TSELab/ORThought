import gurobipy as gp
from gurobipy import GRB
import math

def solve_vehicle_routing(
    customer_num=12,
    truck_num=5,
    truck_capacity=15,
    node_coordinates=[
        (0, 0), (4.36, -2.75), (-7.29, -3.22), (-8.74, -2.47),
        (-0.68, -5.15), (-0.39, -3.49), (-6.06, -5.52),
        (-2.67, 9.32), (9.91, 7.87), (2.03, -2.98), (2.33, -1.47),
        (5.1, -2.08), (-8.04, -9.78)
    ],
    customer_demand=[6, 7, 1, 10, 8, 7, 3, 6, 5, 2, 4, 4]
):
    """
    Solves the vehicle routing problem.
    """
    model = gp.Model("VehicleRoutingProblem")

    center = 0
    customers = range(1, customer_num + 1)
    nodes = [center] + list(customers)
    trucks = range(1, truck_num + 1)

    distance = {}
    for i in nodes:
        for j in nodes:
            if i != j:
                x1, y1 = node_coordinates[i]
                x2, y2 = node_coordinates[j]
                distance[i, j] = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    x = {}
    for i in nodes:
        for j in nodes:
            if i != j:
                for k in trucks:
                    x[i, j, k] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}_{k}")

    objective = gp.quicksum(distance[i, j] * x[i, j, k] for i in nodes for j in nodes for k in trucks if i != j)
    model.setObjective(objective, GRB.MINIMIZE)

    for j in customers:
        model.addConstr(gp.quicksum(x[i, j, k] for i in nodes if i != j for k in trucks) == 1, name=f"customer_visited_{j}")

    for i in customers:
        for k in trucks:
            model.addConstr(gp.quicksum(x[i, j, k] for j in nodes if i != j) - gp.quicksum(x[j, i, k] for j in nodes if i != j) == 0, name=f"flow_conservation_{i}_{k}")

    for k in trucks:
        model.addConstr(gp.quicksum(x[center, j, k] for j in customers) <= 1, name=f"truck_{k}_leaves_center")
        model.addConstr(gp.quicksum(x[center, j, k] for j in customers) == gp.quicksum(x[j, center, k] for j in customers), name=f"truck_{k}_returns_center")

    for k in trucks:
        model.addConstr(gp.quicksum(customer_demand[j - 1] * gp.quicksum(x[i, j, k] for i in nodes if i != j) for j in customers) <= truck_capacity, name=f"truck_{k}_capacity")

    def find_subtours(x_vals, k):
        edges = [(i, j) for i in customers for j in customers if i != j and x_vals.get((i, j, k), 0) > 0.5]
        if not edges:
            return []
        
        neighbors = {i: [] for i in customers}
        for i, j in edges:
            neighbors[i].append(j)
        
        unvisited = set(customers)
        subtours = []
        while unvisited:
            curr = next(iter(unvisited))
            tour = [curr]
            unvisited.remove(curr)
            
            while True:
                neighbors_of_curr = [j for j in neighbors.get(curr, []) if j in unvisited]
                if not neighbors_of_curr:
                    break
                curr = neighbors_of_curr[0]
                tour.append(curr)
                unvisited.remove(curr)
            
            is_valid_tour = any(x_vals.get((center, i, k), 0) > 0.5 for i in tour) and any(x_vals.get((i, center, k), 0) > 0.5 for i in tour)
            if not is_valid_tour and tour:
                subtours.append(tour)
        return subtours

    def subtour_elimination_callback(model, where):
        if where == GRB.Callback.MIPSOL:
            x_vals = model.cbGetSolution(x)
            for k in trucks:
                subtours = find_subtours(x_vals, k)
                for subtour in subtours:
                    if len(subtour) < customer_num:
                        model.cbLazy(gp.quicksum(x[i, j, k] for i in subtour for j in subtour if i != j) <= len(subtour) - 1)

    model.Params.lazyConstraints = 1
    model.optimize(subtour_elimination_callback)

    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.objVal}
    else:
        return {"status": f"{model.status}"}

if __name__ == "__main__":
    result = solve_vehicle_routing()
    print(result)

