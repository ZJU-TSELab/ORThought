def optimize_transportation():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("ThemeParkTransport")

    # Decision variables
    s = m.addVar(name="scooters", vtype=GRB.INTEGER, lb=0)
    r = m.addVar(name="rickshaws", vtype=GRB.INTEGER, lb=0)

    # Set objective: minimize number of scooters
    m.setObjective(s, GRB.MINIMIZE)

    # Capacity constraint: at least 300 visitors
    m.addConstr(2 * s + 3 * r >= 300, name="capacity")

    # Pollution constraint: r ≤ (2/3) * s
    m.addConstr(r <= (2/3) * s, name="pollution_limit")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimal number of scooters used
        return s.X
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_scooters = optimize_transportation()
    if min_scooters is not None:
        print(f"Minimum Number of Scooters: {min_scooters}")
    else:
        print("No feasible solution found.")