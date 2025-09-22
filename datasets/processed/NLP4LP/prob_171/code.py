def optimize_fish_transport():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("FishTransport")

    # Decision variables
    h = m.addVar(vtype=GRB.INTEGER, name="helicopter_trips", lb=0, ub=5)
    c = m.addVar(vtype=GRB.INTEGER, name="car_trips", lb=0)

    # Set objective: minimize total time
    m.setObjective(40 * h + 30 * c, GRB.MINIMIZE)

    # Add constraints
    # Fish transported constraint
    m.addConstr(30 * h + 20 * c >= 300, name="fish_transport")
    # Trip proportion constraint
    m.addConstr(c >= 1.5 * h, name="car_min_trips")
    # h <= 5 is already enforced by ub=5
    # Non-negativity is enforced by lb=0

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total time
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_time = optimize_fish_transport()
    if min_time is not None:
        print(f"Minimum Total Time: {min_time}")
    else:
        print("No feasible solution found.")