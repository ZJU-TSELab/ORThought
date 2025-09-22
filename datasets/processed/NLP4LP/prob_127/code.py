def optimize_medicine_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("MedicineProduction")

    # Decision variables
    x = m.addVar(vtype=GRB.INTEGER, name="x")  # Doses of medicine A
    y = m.addVar(vtype=GRB.INTEGER, name="y")  # Doses of medicine B

    # Set objective: maximize total treated people
    m.setObjective(12 * x + 8 * y, GRB.MAXIMIZE)

    # Add constraints
    m.addConstr(30 * x + 40 * y <= 300, "MaterialConstraint")
    m.addConstr(50 * x + 30 * y <= 400, "mRNAConstraint")
    m.addConstr(x <= 5, "MaxDosesA")
    m.addConstr(y >= x + 1, "B_at_least_A")
    m.addConstr(x >= 0, "NonNegX")
    m.addConstr(y >= 0, "NonNegY")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum number of people treated
        return m.objVal
    else:
        return None

print(optimize_medicine_production())