def optimize_transportation():
    from gurobipy import Model, GRB

    # Parameters
    total_produce = 1000
    pollution_limit = 1000
    min_horse_trips = 8
    capacity_horse = 55
    capacity_bicycle = 30
    capacity_handcart = 40
    pollution_horse = 80
    M = 1000  # Large number for linking constraints

    # Create model
    m = Model("FarmerTransport")

    # Decision variables
    x_H = m.addVar(vtype=GRB.INTEGER, lb=min_horse_trips, name="x_H")
    x_B = m.addVar(vtype=GRB.INTEGER, lb=0, name="x_B")
    x_C = m.addVar(vtype=GRB.INTEGER, lb=0, name="x_C")
    y_B = m.addVar(vtype=GRB.BINARY, name="y_B")
    y_C = m.addVar(vtype=GRB.BINARY, name="y_C")

    m.update()

    # Objective: Minimize pollution from horse trips
    m.setObjective(pollution_horse * x_H, GRB.MINIMIZE)

    # Constraints
    # Produce transportation
    m.addConstr(
        capacity_horse * x_H + capacity_bicycle * x_B + capacity_handcart * x_C
        >= total_produce, "ProduceTransport")
    # Pollution limit
    m.addConstr(pollution_horse * x_H <= pollution_limit, "PollutionLimit")
    # Mode selection
    m.addConstr(y_B + y_C == 1, "ModeSelection")
    # Linking trips to mode selection
    m.addConstr(x_B <= M * y_B, "LinkBicycle")
    m.addConstr(x_C <= M * y_C, "LinkHandcart")
    # Minimum horse trips
    m.addConstr(x_H >= min_horse_trips, "MinHorseTrips")

    # Optimize
    m.optimize()

    # Check feasibility and return result
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