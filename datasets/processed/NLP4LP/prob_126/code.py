def optimize_fruit_intake():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Fruit_Optimization")

    # Decision variables: number of oranges and grapefruits
    x = m.addVar(name="oranges", lb=0, vtype=GRB.INTEGER)
    y = m.addVar(name="grapefruits", lb=0, vtype=GRB.INTEGER)

    # Set the objective: minimize total sugar intake
    m.setObjective(5 * x + 6 * y, GRB.MINIMIZE)

    # Add vitamin C constraint
    m.addConstr(5 * x + 7 * y >= 80, name="VitaminC")
    # Add vitamin A constraint
    m.addConstr(3 * x + 5 * y >= 70, name="VitaminA")
    # Add preference constraint: oranges at least twice grapefruits
    m.addConstr(x - 2 * y >= 0, name="Preference")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal objective value (minimum sugar intake)
        return m.objVal
    else:
        # No feasible solution found
        return None

# Example usage
print(optimize_fruit_intake())