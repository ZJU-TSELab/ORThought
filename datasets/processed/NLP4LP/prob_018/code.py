def optimize_candy_mixes(
    regular_candy_available=80,
    sour_candy_available=60,
    profit_regular_mix=3,
    profit_sour_surprise=5
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Candy_Mix_Optimization")

    # Decision variables: amount of each mix to produce
    x = model.addVar(name="Regular_Mix", lb=0)
    y = model.addVar(name="Sour_Surprise_Mix", lb=0)

    # Set objective: maximize profit
    model.setObjective(profit_regular_mix * x + profit_sour_surprise * y, GRB.MAXIMIZE)

    # Add constraints
    # Regular candy constraint
    model.addConstr(0.8 * x + 0.1 * y <= regular_candy_available, name="Regular_Candy_Constraint")
    # Sour candy constraint
    model.addConstr(0.2 * x + 0.9 * y <= sour_candy_available, name="Sour_Candy_Constraint")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal profit value
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_candy_mixes()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")