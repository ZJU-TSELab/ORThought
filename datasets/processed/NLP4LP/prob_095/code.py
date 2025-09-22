def optimize_factory_hours():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Factory_Production_MinHours")

    # Decision variables: hours to run each factory
    x1 = m.addVar(name="x1", lb=0)
    x2 = m.addVar(name="x2", lb=0)
    max_hour = m.addVar(name="max_hour", lb=0)

    # Set the objective: minimize total hours
    m.setObjective(max_hour, GRB.MINIMIZE)

    # Add production constraints
    m.addConstr(20 * x1 + 10 * x2 >= 700, name="Allergy_Pills")
    m.addConstr(15 * x1 + 30 * x2 >= 600, name="Fever_Pills")

    # Add resource constraint
    m.addConstr(20 * x1 + 30 * x2 <= 1000, name="Rare_Compound")

    # Add maximum hour constraint
    m.addConstr(max_hour >= x1, name="Max_Hour_x1")
    m.addConstr(max_hour >= x2, name="Max_Hour_x2")
    
    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total hours
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
print(optimize_factory_hours())