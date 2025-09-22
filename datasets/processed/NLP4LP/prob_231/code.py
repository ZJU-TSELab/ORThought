def optimize_meals():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Salmon_Egg_Optimization")

    # Decision variables: number of salmon and eggs bowls
    x_s = m.addVar(name="Salmon", lb=0, vtype=GRB.INTEGER)
    x_e = m.addVar(name="Eggs", lb=0, vtype=GRB.INTEGER)

    # Set the objective: minimize total sodium intake
    sodium = 80 * x_s + 20 * x_e
    m.setObjective(sodium, GRB.MINIMIZE)

    # Add calorie constraint
    m.addConstr(300 * x_s + 200 * x_e >= 2000, name="Calories")

    # Add protein constraint
    m.addConstr(15 * x_s + 8 * x_e >= 90, name="Protein")

    # Add egg proportion constraint: x_e <= (2/3) * x_s
    m.addConstr(x_e <= (2/3) * x_s, name="EggProportion")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal sodium intake
        return m.objVal
    else:
        # No feasible solution
        return None

# Example usage
print(optimize_meals())
