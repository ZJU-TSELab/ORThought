import gurobipy as gp
from gurobipy import GRB


def solve_warehouse_location(
    CustomerZones=['C1', 'C2', 'C3', 'C4', 'C5'],
    WarehouseLocations=['W1', 'W2', 'W3'],
    DistanceMatrix={
        'W1': {'C1': 10, 'C2': 15, 'C3': 12, 'C4': 8, 'C5': 20},
        'W2': {'C1': 8, 'C2': 10, 'C3': 15, 'C4': 12, 'C5': 18},
        'W3': {'C1': 12, 'C2': 8, 'C3': 10, 'C4': 15, 'C5': 12}
    },
    p=2
):
    """Solve the warehouse location selection problem using Gurobi."""
    # Create a new model
    model = gp.Model("WarehouseLocation")

    # Decision variables
    y = model.addVars(WarehouseLocations, vtype=GRB.BINARY, name="Open")
    x = model.addVars(WarehouseLocations, CustomerZones, vtype=GRB.BINARY, name="Assign")

    # Objective: Minimize total distance
    model.setObjective(
        gp.quicksum(DistanceMatrix[w][c] * x[w, c] for w in WarehouseLocations for c in CustomerZones),
        GRB.MINIMIZE
    )

    # Constraints
    model.addConstr(gp.quicksum(y[w] for w in WarehouseLocations) == p, "Open_p_warehouses")
    for c in CustomerZones:
        model.addConstr(gp.quicksum(x[w, c] for w in WarehouseLocations) == 1, f"Assign_one_warehouse_{c}")
    for w in WarehouseLocations:
        for c in CustomerZones:
            model.addConstr(x[w, c] <= y[w], f"Assign_only_if_open_{w}_{c}")

    # Optimize the model
    model.optimize()

    # Return results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_warehouse_location()
    print(result)