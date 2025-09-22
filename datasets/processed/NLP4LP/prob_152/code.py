def optimize_cow_transport():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("CowTransport")

    # Decision variables
    h = m.addVar(vtype=GRB.INTEGER, name="HelicopterTrips", lb=0)
    t = m.addVar(vtype=GRB.INTEGER, name="TruckTrips", lb=0)

    # Set objective: minimize total pollution
    m.setObjective(5 * h + 10 * t, GRB.MINIMIZE)

    # Add constraints
    # Ensure at least 80 cows are transported
    m.addConstr(3 * h + 7 * t >= 80, "CowsTransported")
    # Limit on number of truck trips
    m.addConstr(t <= 8, "TruckLimit")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total pollution
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_pollution = optimize_cow_transport()
    if min_pollution is not None:
        print(f"Minimum Total Pollution: {min_pollution}")
    else:
        print("No feasible solution found.")