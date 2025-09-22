def optimize_meal_plan():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("MealReplacementOptimization")

    # Decision variables: number of bottles of alpha and omega
    x = m.addVar(name="alpha_bottles", lb=0, vtype=GRB.INTEGER)
    y = m.addVar(name="omega_bottles", lb=0, vtype=GRB.INTEGER)

    # Set the objective: minimize total sugar
    m.setObjective(20 * x + 15 * y, GRB.MINIMIZE)

    # Add protein constraint
    m.addConstr(30 * x + 20 * y >= 100, name="protein_req")

    # Add calorie constraint
    m.addConstr(350 * x + 300 * y >= 2000, name="calorie_req")

    # Add omega proportion constraint
    # y <= (0.35/0.65) * x
    m.addConstr(y <= (0.35 / 0.65) * x, name="omega_ratio")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal sugar intake
        return m.objVal
    else:
        # No feasible solution
        return None

# Example usage
print(optimize_meal_plan())