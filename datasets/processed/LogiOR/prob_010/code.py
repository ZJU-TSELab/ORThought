import gurobipy as gp
from gurobipy import GRB


def solve_p_center(
    distance=[
        [15, 22, 30, 45, 50, 12, 28, 35, 40, 25],
        [10, 18, 25, 35, 40, 8, 20, 28, 32, 18],
        [25, 30, 35, 50, 55, 22, 32, 40, 45, 30],
        [30, 35, 40, 55, 60, 25, 35, 45, 50, 35],
        [5, 12, 20, 30, 35, 5, 15, 22, 28, 12]
    ],
    select_location_num=2
):
    """
    Models and solves the P-Center facility location problem.
    """
    # --- 1. Model Creation ---
    model = gp.Model("P-Center-Problem")

    # --- 2. Sets ---
    # Derive sets from the dimensions of the input data
    candidate_locations = range(len(distance))
    outlets = range(len(distance[0]))

    # --- 3. Decision Variables ---
    # x[i] = 1 if location i is selected, 0 otherwise
    x = model.addVars(candidate_locations, vtype=GRB.BINARY, name="select_location")

    # z = auxiliary variable for the min-max objective (maximum distance)
    z = model.addVar(vtype=GRB.CONTINUOUS, name="max_distance")

    # y[i, j] = 1 if outlet j is assigned to location i, 0 otherwise
    y = model.addVars(candidate_locations, outlets, vtype=GRB.BINARY, name="assign")

    # --- 4. Objective Function ---
    # Minimize the maximum distance (z)
    model.setObjective(z, GRB.MINIMIZE)

    # --- 5. Constraints ---
    # Constraint 1: Select exactly 'p' (select_location_num) locations
    model.addConstr(gp.quicksum(x[i] for i in candidate_locations) == select_location_num,
                    name="p_selection")

    # Constraint 2: Each outlet must be assigned to exactly one location
    for j in outlets:
        model.addConstr(gp.quicksum(y[i, j] for i in candidate_locations) == 1,
                        name=f"outlet_assignment_{j}")

    # Constraint 3: An outlet can only be assigned to a selected (opened) location
    for i in candidate_locations:
        for j in outlets:
            model.addConstr(y[i, j] <= x[i], name=f"valid_assignment_{i}_{j}")

    # Constraint 4: Define the maximum distance 'z'
    # If outlet j is assigned to location i (y[i,j]=1), then z must be at least
    # as large as the distance between them.
    for i in candidate_locations:
        for j in outlets:
            model.addConstr(z >= distance[i][j] * y[i, j],
                            name=f"max_distance_link_{i}_{j}")

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
    result = solve_p_center()
    print(result)
