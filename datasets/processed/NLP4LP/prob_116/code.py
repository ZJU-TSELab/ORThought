def optimize_nut_intake():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("nut_intake_min_fat")

    # Decision variables: servings of almonds and cashews
    x_A = m.addVar(name="almond_servings", lb=0)
    x_C = m.addVar(name="cashew_servings", lb=0)

    # Set the objective: minimize total fat intake
    m.setObjective(15 * x_A + 12 * x_C, GRB.MINIMIZE)

    # Add constraints
    # Calorie constraint
    m.addConstr(200 * x_A + 300 * x_C >= 10000, name="calories")
    # Protein constraint
    m.addConstr(20 * x_A + 25 * x_C >= 800, name="protein")
    # Servings ratio constraint
    m.addConstr(x_A >= 2 * x_C, name="ratio")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal value of the objective function
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_fat = optimize_nut_intake()
    if min_fat is not None:
        print(f"Minimum Total Fat Intake: {min_fat}")
    else:
        print("No feasible solution found.")