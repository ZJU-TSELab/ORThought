def optimize_wraps_and_platters():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("FastFoodProduction")

    # Decision variables: number of wraps (x) and platters (y)
    x = m.addVar(vtype=GRB.INTEGER, name="wraps", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="platters", lb=0)

    # Set objective: minimize total production time
    m.setObjective(10 * x + 8 * y, GRB.MINIMIZE)

    # Add resource constraints
    m.addConstr(5 * x + 7 * y >= 3000, name="meat_constraint")
    m.addConstr(3 * x + 5 * y >= 2500, name="rice_constraint")

    # Add production ratio constraint
    m.addConstr(x - 3 * y >= 0, name="wraps_vs_platters")

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
    min_time = optimize_wraps_and_platters()
    if min_time is not None:
        print(f"Minimum Total Production Time: {min_time}")
    else:
        print("No feasible solution found.")