def optimize_meal_plan():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("MealOptimization")

    # Decision variables: number of fish and chicken meals
    x = m.addVar(name="fish_meals", lb=0, vtype=GRB.INTEGER)
    y = m.addVar(name="chicken_meals", lb=0, vtype=GRB.INTEGER)

    # Set the objective: minimize total fat intake
    m.setObjective(7 * x + 10 * y, GRB.MINIMIZE)

    # Add constraints
    # Protein constraint
    m.addConstr(10 * x + 15 * y >= 130, name="protein_req")
    # Iron constraint
    m.addConstr(12 * x + 8 * y >= 120, name="iron_req")
    # Preference constraint
    m.addConstr(y >= 2 * x, name="chicken_pref")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total fat intake
        return m.objVal
    else:
        # No feasible solution
        return None

# Example usage
print(optimize_meal_plan())