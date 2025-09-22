def optimize_diet():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("DietOptimization")

    # Decision variables: servings of noodles (x) and protein bars (y)
    x = m.addVar(name="noodles", lb=0)
    y = m.addVar(name="protein_bars", lb=0)

    # Set the objective: minimize total cost
    m.setObjective(5 * x + 2.5 * y, GRB.MINIMIZE)

    # Add calorie constraint
    m.addConstr(600 * x + 250 * y >= 2000, name="calories")
    # Add protein constraint
    m.addConstr(1.5 * x + 5 * y >= 16, name="protein")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal cost
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_cost = optimize_diet()
    if min_cost is not None:
        print(f"Minimum Cost: {min_cost}")
    else:
        print("No feasible solution found.")