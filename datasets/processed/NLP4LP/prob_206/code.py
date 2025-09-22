def optimize_snacks():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("SnackMixOptimization")

    # Decision variables: amount of each mix to produce
    x1 = m.addVar(name="x1", lb=0)  # first mix
    x2 = m.addVar(name="x2", lb=0)  # second mix

    # Set the objective: maximize profit
    profit = 12 * x1 + 15 * x2
    m.setObjective(profit, GRB.MAXIMIZE)

    # Add constraints
    # Cat paw snack constraint
    m.addConstr(0.20 * x1 + 0.35 * x2 <= 20, name="CatPawConstraint")
    # Gold shark snack constraint
    m.addConstr(0.80 * x1 + 0.65 * x2 <= 50, name="GoldSharkConstraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum profit
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_snacks()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")