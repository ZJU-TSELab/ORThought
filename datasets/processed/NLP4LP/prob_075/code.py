def optimize_coffee_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("CoffeeProduction")

    # Decision variables: number of mochas (x) and regular coffees (y)
    x = m.addVar(vtype=GRB.INTEGER, name="mochas", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="regular_coffees", lb=0)

    # Set the objective: minimize total production time
    m.setObjective(5 * x + 3 * y, GRB.MINIMIZE)

    # Add resource constraints
    m.addConstr(3 * x + 6 * y <= 400, name="coffee_powder")
    m.addConstr(6 * x + 2 * y <= 500, name="milk")

    # Add production ratio constraint
    m.addConstr(x >= 3 * y, name="mocha_ratio")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total production time
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_time = optimize_coffee_production()
    if min_time is not None:
        print(f"Minimum Total Production Time: {min_time}")
    else:
        print("No feasible solution found.")