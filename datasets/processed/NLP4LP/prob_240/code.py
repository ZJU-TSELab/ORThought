def optimize_candle_transport():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Candle_Transport")

    # Decision variables
    # Number of freight trips (F), at least 5
    F = m.addVar(vtype=GRB.INTEGER, name="F", lb=5)
    # Number of air trips (A), at least 0
    A = m.addVar(vtype=GRB.INTEGER, name="A", lb=0)

    # Set objective: minimize total trips
    m.setObjective(F + A, GRB.MINIMIZE)

    # Add constraints
    # Total tons transported
    m.addConstr(5 * F + 3 * A >= 200, name="TotalTons")
    # Budget constraint
    m.addConstr(300 * F + 550 * A <= 20000, name="Budget")
    # Air transportation proportion constraint
    # A >= (1.5/2.1)*F
    m.addConstr(A >= (1.5 / 2.1) * F, name="AirProportion")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        total_trips = m.objVal
        return total_trips
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_trips = optimize_candle_transport()
    if min_trips is not None:
        print(f"Minimum Total Trips (Freight + Air): {min_trips}")
    else:
        print("No feasible solution found.")