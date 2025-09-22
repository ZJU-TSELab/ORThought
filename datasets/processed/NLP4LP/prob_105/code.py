def optimize_factory_hours():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("FactoryOptimization")

    # Decision variables: hours each factory runs
    t1 = m.addVar(name="t1", lb=0)
    t2 = m.addVar(name="t2", lb=0)
    max_hour = m.addVar(name="max_hour", lb=0)

    # Set the objective: minimize total hours
    m.setObjective(max_hour, GRB.MINIMIZE)

    # Add constraints
    # Acne cream production constraint
    m.addConstr(12 * t1 + 20 * t2 >= 800, name="AcneProduction")
    # Anti-bacterial cream production constraint
    m.addConstr(15 * t1 + 10 * t2 >= 1000, name="AntiBacterialProduction")
    # Base gel resource constraint
    m.addConstr(30 * t1 + 45 * t2 <= 5000, name="BaseGelLimit")
    # Maximum hours constraint
    m.addConstr(t1 <= max_hour, name="MaxHoursT1")
    m.addConstr(t2 <= max_hour, name="MaxHoursT2")
    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total hours
        return m.objVal
    else:
        # No feasible solution
        return None

# Example usage
print(optimize_factory_hours())