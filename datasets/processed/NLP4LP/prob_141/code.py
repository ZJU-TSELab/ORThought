def optimize_duck_transport():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("DuckTransport")

    # Decision variables: number of trips
    x_b = m.addVar(vtype=GRB.INTEGER, name="boat_trips")
    x_c = m.addVar(vtype=GRB.INTEGER, name="canoe_trips")

    # Set objective: minimize total time
    m.setObjective(20 * x_b + 40 * x_c, GRB.MINIMIZE)

    # Add constraints
    # Ducks transported at least 300
    m.addConstr(10 * x_b + 8 * x_c >= 300, name="duck_transport")
    # Maximum 12 boat trips
    m.addConstr(x_b <= 12, name="max_boat_trips")
    # At least 60% trips are by canoe
    m.addConstr(2 * x_c >= 3 * x_b, name="canoe_ratio")
    # Non-negativity (implicitly enforced by variable type)
    # (Gurobi variables are non-negative by default unless specified otherwise)

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimal total time
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_time = optimize_duck_transport()
    if min_time is not None:
        print(f"Minimum Total Time: {min_time}")
    else:
        print("No feasible solution found.")