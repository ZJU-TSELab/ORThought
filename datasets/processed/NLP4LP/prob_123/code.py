def optimize_cakes():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("CakeEatingOptimization")

    # Decision variables
    # x: number of cheesecake slices
    # y: number of caramel cake slices
    x = m.addVar(vtype=GRB.INTEGER, name="x", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="y", lb=0)

    # Set objective: maximize sugar intake
    m.setObjective(40 * x + 50 * y, GRB.MAXIMIZE)

    # Add constraints
    # Preference constraint: x >= 3y
    m.addConstr(x >= 3 * y, "pref_constraint")
    # Minimum caramel slices
    m.addConstr(y >= 3, "min_caramel")
    # Calorie constraint
    m.addConstr(200 * x + 250 * y <= 10000, "calorie_limit")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum sugar intake
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_sugar = optimize_cakes()
    if max_sugar is not None:
        print(f"Maximum Sugar Intake: {max_sugar}")
    else:
        print("No feasible solution found.")