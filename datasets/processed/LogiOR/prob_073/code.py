import gurobipy as gp
from gurobipy import GRB

def solve_delivery_routing(
    trucks=[1, 2, 3],
    stores=[1, 2, 3, 4, 5],
    truck_capacities={1: 8, 2: 10, 3: 12},
    store_demands={1: 3, 2: 4, 3: 5, 4: 2, 5: 6},
    distances={1: 15, 2: 20, 3: 25, 4: 30, 5: 35}
):
    """
    Solves the delivery routing optimization problem using Gurobi.
    Minimizes total distance traveled by trucks while meeting store demands and truck capacity constraints.
    """
    # Create model
    model = gp.Model("DeliveryRouting")

    # Decision variables
    # Binary variable indicating if truck t is used
    truck_used = model.addVars(trucks, vtype=GRB.BINARY, name="truck_used")
    # Binary variable indicating if store s is assigned to truck t
    store_assignment = model.addVars(stores, trucks, vtype=GRB.BINARY, name="store_assignment")
    # Continuous variable for distance traveled by each truck
    route_distance = model.addVars(trucks, lb=0, vtype=GRB.CONTINUOUS, name="route_distance")

    # Objective: Minimize total distance traveled by all trucks
    model.setObjective(
        gp.quicksum(route_distance[t] for t in trucks),
        GRB.MINIMIZE
    )

    # Constraints
    # 1. Each store must be assigned to exactly one truck
    model.addConstrs(
        (store_assignment.sum(s, '*') == 1 for s in stores),
        name="store_assignment"
    )

    # 2. Truck capacity cannot be exceeded
    model.addConstrs(
        (gp.quicksum(store_demands[s] * store_assignment[s, t] for s in stores) <= truck_capacities[t]
         for t in trucks),
        name="truck_capacity"
    )

    # 3. Distance calculation (truck distance is distance to farthest store visited)
    model.addConstrs(
        (route_distance[t] >= distances[s] * store_assignment[s, t]
         for s in stores for t in trucks),
        name="distance_calc"
    )

    # 4. Truck usage constraint (if any store is assigned to truck)
    model.addConstrs(
        (gp.quicksum(store_assignment[s, t] for s in stores) <= len(stores) * truck_used[t]
         for t in trucks),
        name="truck_usage"
    )

    # Optimize model
    model.optimize()

    # Return results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_delivery_routing()
    print(result)