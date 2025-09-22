def optimize_transportation():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("TransportationOptimization")

    # Decision variables
    T = m.addVar(name="TruckTrips", lb=10, vtype=GRB.INTEGER)
    V = m.addVar(name="VanTrips", lb=0, vtype=GRB.INTEGER)
    M = m.addVar(name="MotorcycleTrips", lb=0, vtype=GRB.INTEGER)
    E = m.addVar(name="ElectricTrips", lb=0, vtype=GRB.INTEGER)

    y_V = m.addVar(name="UseVan", vtype=GRB.BINARY)
    y_E = m.addVar(name="UseElectric", vtype=GRB.BINARY)

    m.update()

    # Set objective: minimize total pollution
    m.setObjective(100 * T + 50 * V * y_V + 10 * M, GRB.MINIMIZE)

    # Constraints
    # Total units transported
    m.addConstr(100 * T + 80 * V * y_V + 40 * M + 60 * E * y_E >= 1800,
                name="Demand")

    # Pollution limit
    m.addConstr(100 * T + 50 * V * y_V + 10 * M <= 2000, name="PollutionLimit")

    # Van/Electric vehicle exclusivity
    m.addConstr(y_V + y_E <= 1, name="ModeChoice")

    # Minimum truck trips
    m.addConstr(T >= 10, name="MinTruckTrips")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
if __name__ == "__main__":
    result = optimize_transportation()
    if result is not None:
        print(f"Optimal total pollution: {result}")
    else:
        print("No feasible solution found.")