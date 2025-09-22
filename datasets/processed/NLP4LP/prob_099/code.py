def optimize_syrup_intake():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("SyrupOptimization")

    # Decision variables: number of servings of each syrup
    x1 = m.addVar(name="x1", lb=0)
    x2 = m.addVar(name="x2", lb=0)

    # Set the objective: minimize sugar intake
    m.setObjective(0.5 * x1 + 0.3 * x2, GRB.MINIMIZE)

    # Add constraints
    m.addConstr(0.5 * x1 + 0.2 * x2 <= 5, name="ThroatMedicine")
    m.addConstr(0.4 * x1 + 0.5 * x2 >= 4, name="LungMedicine")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None

# Example usage
print(optimize_syrup_intake())