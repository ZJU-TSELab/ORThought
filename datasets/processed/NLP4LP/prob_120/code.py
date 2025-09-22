def optimize_gorilla_fruits():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("GorillaFruits")

    # Decision variables: number of bananas and mangoes
    x_b = m.addVar(name="Bananas", lb=0, vtype=GRB.INTEGER)
    x_m = m.addVar(name="Mangoes", lb=0, vtype=GRB.INTEGER)

    # Set the objective: minimize total sugar intake
    m.setObjective(10 * x_b + 8 * x_m, GRB.MINIMIZE)

    # Add calorie constraint
    m.addConstr(80 * x_b + 100 * x_m >= 4000, name="Calories")
    # Add potassium constraint
    m.addConstr(20 * x_b + 15 * x_m >= 150, name="Potassium")
    # Add preference constraint (x_b >= 2 * x_m)
    m.addConstr(x_b >= 2 * x_m, name="Preference")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimum sugar intake
        return m.objVal
    else:
        # No feasible solution
        return None

# Example usage
print(optimize_gorilla_fruits())