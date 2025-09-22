def optimize_medicine_purchase():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("MedicineOptimization")

    # Decision variables: number of pills to buy
    x_z = m.addVar(name="Zodiac", lb=0, vtype=GRB.INTEGER)
    x_s = m.addVar(name="Sunny", lb=0, vtype=GRB.INTEGER)

    # Set objective: minimize total cost
    m.setObjective(x_z + 3 * x_s, GRB.MINIMIZE)

    # Add constraints
    # Z1 requirement
    m.addConstr(1.3 * x_z + 1.2 * x_s >= 5, name="Z1_requirement")
    # D3 requirement
    m.addConstr(1.5 * x_z + 5 * x_s >= 10, name="D3_requirement")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None

print(optimize_medicine_purchase())