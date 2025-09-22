def optimize_cholesterol():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Minimize Cholesterol Intake")

    # Decision variables: number of burgers (x) and slices of pizza (y)
    # Both are integers and >= 0
    x = m.addVar(name="burgers", vtype=GRB.INTEGER, lb=0)
    y = m.addVar(name="pizza_slices", vtype=GRB.INTEGER, lb=0)

    # Set the objective: minimize total cholesterol
    m.setObjective(12 * x + 10 * y, GRB.MINIMIZE)

    # Add constraints
    m.addConstr(10 * x + 8 * y >= 130, name="fat_constraint")
    m.addConstr(300 * x + 250 * y >= 3000, name="calorie_constraint")
    m.addConstr(y >= 2 * x, name="pizza_burger_ratio")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_cholesterol = optimize_cholesterol()
    if min_cholesterol is not None:
        print(f"Minimum Cholesterol Intake: {min_cholesterol}")
    else:
        print("No feasible solution found.")