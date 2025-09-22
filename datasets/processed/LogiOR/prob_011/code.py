import gurobipy as gp
from gurobipy import GRB


def solve_drone_hub_location(
    demand_nodes=[(10, 20), (25, 60), (40, 80), (65, 50), (80, 20), (15, 45),
                  (70, 75), (90, 90)],
    num_hubs=2,
    hub_coordinates_range=[[0, 100], [0, 100]],
    big_m=20000
):
    """
    Models and solves the drone hub location problem (a type of P-Center problem
    in a continuous space).
    """
    # --- 1. Model Creation ---
    model = gp.Model("DroneHubLocation")
    # This parameter is crucial for Gurobi to solve non-convex quadratic problems
    model.Params.NonConvex = 2

    # --- 2. Sets and Parameters ---
    num_demands = len(demand_nodes)
    hubs = range(num_hubs)
    demands = range(num_demands)
    xl, xu = hub_coordinates_range[0]
    yl, yu = hub_coordinates_range[1]

    # --- 3. Decision Variables ---
    # hub_x, hub_y: coordinates of the selected hubs
    hub_x = model.addVars(hubs, lb=xl, ub=xu, name="HubX")
    hub_y = model.addVars(hubs, lb=yl, ub=yu, name="HubY")
    # a[i,j]: 1 if demand node j is assigned to hub i, 0 otherwise
    a = model.addVars(hubs, demands, vtype=GRB.BINARY, name="Assignment")
    # z: the maximum distance from any demand node to its assigned hub
    z = model.addVar(vtype=GRB.CONTINUOUS, name="MaxDistance")

    # --- 4. Objective Function ---
    # Minimize the maximum distance (z)
    model.setObjective(z, GRB.MINIMIZE)

    # --- 5. Constraints ---
    # Constraint 1: Each demand node must be assigned to exactly one hub
    for j in demands:
        model.addConstr(gp.quicksum(a[i, j] for i in hubs) == 1, f"Assign_{j}")

    # Constraint 2: Link the maximum distance 'z' to the hub locations.
    # This is a non-convex quadratic constraint of the form:
    # (distance_squared) <= z^2, which only applies if a[i,j] = 1.
    for i in hubs:
        for j in demands:
            x_j, y_j = demand_nodes[j]
            dx = hub_x[i] - x_j
            dy = hub_y[i] - y_j
            model.addConstr(dx * dx + dy * dy <= z * z + big_m * (1 - a[i, j]),
                            f"Distance_{i}_{j}")

    # --- 6. Solve the Model ---
    model.setParam("OutputFlag", 0)  # Suppress Gurobi output
    model.optimize()

    # --- 7. Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == "__main__":
    result = solve_drone_hub_location()
    print(result)
