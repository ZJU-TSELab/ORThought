def optimize_trips():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Chocolate_Transport")

    # Decision variables: number of van trips (x) and truck trips (y)
    # Both are integers and >= 0
    x = m.addVar(vtype=GRB.INTEGER, name="van_trips")
    y = m.addVar(vtype=GRB.INTEGER, name="truck_trips")

    # Set the objective: minimize total number of trips
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add capacity constraint: at least 1500 boxes transported
    m.addConstr(50 * x + 80 * y >= 1500, name="capacity_constraint")

    # Add budget constraint: total cost <= 1000
    m.addConstr(30 * x + 50 * y <= 1000, name="budget_constraint")

    # Add trip comparison constraint: van trips > truck trips
    # Since Gurobi does not support strict inequalities directly,
    # we model x > y as x >= y + 1
    m.addConstr(x >= y + 1, name="trip_comparison")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimal total number of trips
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_trips = optimize_trips()
    if min_trips is not None:
        print(f"Minimum Total Trips: {min_trips}")
    else:
        print("No feasible solution found.")