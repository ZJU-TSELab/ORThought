import gurobipy as gp
from gurobipy import GRB
import math

def solve_waste_collection_routing(
    collection_points_num=15,
    truck_num=4,
    truck_capacity=100,
    truck_max_distance=45,
    nodes_coordinates=[
        (0, 0), (3, -8), (-10, -5), (3, 0), (-3, -3), (5, -1),
        (-7, 3), (5, -3), (4, -5), (6, 4), (3, 1), (-10, 0),
        (-2, 7), (-6, -3), (-8, -7), (-1, 8)
    ],
    collection_points_demand=[
        20, 20, 28, 12, 30, 24, 30, 12, 27, 26, 21, 20, 12, 16, 19
    ]
):
    """
    Solves the vehicle routing problem for waste collection.
    """
    model = gp.Model("WasteCollectionRouting")

    dump = 0
    collection_points = range(1, collection_points_num + 1)
    nodes = [dump] + list(collection_points)
    trucks = range(1, truck_num + 1)

    distance = {}
    for i in nodes:
        for j in nodes:
            if i != j:
                x1, y1 = nodes_coordinates[i]
                x2, y2 = nodes_coordinates[j]
                distance[i, j] = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    x = {}
    for i in nodes:
        for j in nodes:
            if i != j:
                for k in trucks:
                    x[i, j, k] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}_{k}")

    objective = gp.quicksum(distance[i, j] * x[i, j, k] for i in nodes for j in nodes for k in trucks if i != j)
    model.setObjective(objective, GRB.MINIMIZE)

    for j in collection_points:
        model.addConstr(gp.quicksum(x[i, j, k] for i in nodes if i != j for k in trucks) == 1, name=f"visit_point_{j}")

    for i in collection_points:
        for k in trucks:
            model.addConstr(gp.quicksum(x[i, j, k] for j in nodes if j != i) - gp.quicksum(x[j, i, k] for j in nodes if j != i) == 0, name=f"flow_conservation_{i}_{k}")

    for k in trucks:
        model.addConstr(gp.quicksum(x[dump, j, k] for j in collection_points) == 1, name=f"truck_{k}_leaves_dump")
        model.addConstr(gp.quicksum(x[j, dump, k] for j in collection_points) == 1, name=f"truck_{k}_returns_dump")

    for k in trucks:
        model.addConstr(gp.quicksum(collection_points_demand[j - 1] * gp.quicksum(x[i, j, k] for i in nodes if i != j) for j in collection_points) <= truck_capacity, name=f"truck_{k}_capacity")

    for k in trucks:
        model.addConstr(gp.quicksum(distance[i, j] * x[i, j, k] for i in nodes for j in nodes if i != j) <= truck_max_distance, name=f"truck_{k}_max_distance")

    def find_subtours(x_vals, k):
        edges = [(i, j) for i in collection_points for j in collection_points if i != j and x_vals.get((i, j, k), 0) > 0.5]
        if not edges:
            return []
        
        neighbors = {i: [] for i in collection_points}
        for i, j in edges:
            neighbors[i].append(j)
        
        unvisited = set(collection_points)
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
            
            is_valid_tour = any(x_vals.get((dump, i, k), 0) > 0.5 for i in tour) and any(x_vals.get((i, dump, k), 0) > 0.5 for i in tour)
            if not is_valid_tour and tour:
                subtours.append(tour)
        return subtours

    def subtour_elimination_callback(model, where):
        if where == GRB.Callback.MIPSOL:
            x_vals = model.cbGetSolution(x)
            for k in trucks:
                subtours = find_subtours(x_vals, k)
                for subtour in subtours:
                    if len(subtour) < collection_points_num:
                        model.cbLazy(gp.quicksum(x[i, j, k] for i in subtour for j in subtour if i != j) <= len(subtour) - 1)

    model.Params.lazyConstraints = 1
    model.optimize(subtour_elimination_callback)

    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.objVal}
    else:
        return {"status": f"{model.status}"}

if __name__ == "__main__":
    result = solve_waste_collection_routing()
    print(result)
