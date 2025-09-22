def solve_aircraft_landing_problem(
    earliest_landing=[1, 3, 5],
    latest_landing=[10, 12, 15],
    target_landing=[4, 8, 14],
    penalty_after_target=[10, 20, 30],
    penalty_before_target=[5, 10, 15],
    separation_time=[[0, 2, 3], [2, 0, 4], [3, 4, 0]],
    order_pairs=None  # Optional: list of (i,j) pairs indicating order i before j
):
    import gurobipy as gp
    from gurobipy import GRB

    n = len(earliest_landing)
    model = gp.Model("AircraftLanding")
    model.Params.OutputFlag = 0  # Silence output

    # Decision variables: landing times
    t = model.addVars(n, lb=0, name="t", vtype=GRB.CONTINUOUS)

    # Auxiliary variables for penalties
    d_minus = model.addVars(n, lb=0, name="d_minus")
    d_plus = model.addVars(n, lb=0, name="d_plus")

    # Set default order pairs if not provided
    if order_pairs is None:
        # Assume the order is given by the sequence 0 -> 1 -> 2
        order_pairs = [(0, 1), (1, 2)]
    # Add separation constraints based on order
    for (i, j) in order_pairs:
        model.addConstr(t[j] >= t[i] + separation_time[i][j], name=f"sep_{i}_{j}")

    # Time window constraints
    for i in range(n):
        model.addConstr(t[i] >= earliest_landing[i], name=f"earliest_{i}")
        model.addConstr(t[i] <= latest_landing[i], name=f"latest_{i}")

    # Penalty linearization constraints
    for i in range(n):
        model.addConstr(t[i] - target_landing[i] <= d_plus[i], name=f"penalty_plus_{i}")
        model.addConstr(target_landing[i] - t[i] <= d_minus[i], name=f"penalty_minus_{i}")

    # Objective: minimize total penalties
    total_penalty = gp.quicksum(
        penalty_before_target[i] * d_minus[i] + penalty_after_target[i] * d_plus[i]
        for i in range(n)
    )
    model.setObjective(total_penalty, GRB.MINIMIZE)

    # Optimize
    model.optimize()

    if model.status == GRB.OPTIMAL:
        # Return the total penalty value
        return model.objVal
    else:
        # No feasible solution found
        return None
if __name__ == "__main__":
    result = solve_aircraft_landing_problem()
    print(f"Minimum total penalty: {result}")