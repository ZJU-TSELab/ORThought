def optimize_transport_infrastructure():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("AirportTransport")

    # Decision variables
    # Number of escalators
    x = m.addVar(vtype=GRB.INTEGER, name="Escalators", lb=0)
    # Number of elevators
    y = m.addVar(vtype=GRB.INTEGER, name="Elevators", lb=0)

    # Set objective: minimize total space
    m.setObjective(5 * x + 2 * y, GRB.MINIMIZE)

    # Capacity constraint
    m.addConstr(20 * x + 8 * y >= 400, name="Capacity")

    # Ratio constraint: at least three times more escalators than elevators
    m.addConstr(x >= 3 * y, name="Ratio")

    # Minimum number of elevators
    m.addConstr(y >= 2, name="MinElevators")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total space
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_space = optimize_transport_infrastructure()
    if min_space is not None:
        print(f"Minimum Total Space: {min_space}")
    else:
        print("No feasible solution found.")