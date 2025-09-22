def optimize_handbags(
    profit_regular=30,
    profit_premium=180,
    cost_regular=200,
    cost_premium=447,
    total_budget=250000,
    max_total_handbags=475
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Handbag_Production_Optimization")

    # Decision variables: number of regular and premium handbags
    x = model.addVar(vtype=GRB.INTEGER, name="Regular_Handbags", lb=0)
    y = model.addVar(vtype=GRB.INTEGER, name="Premium_Handbags", lb=0)

    # Set objective: maximize profit
    model.setObjective(profit_regular * x + profit_premium * y, GRB.MAXIMIZE)

    # Add budget constraint
    model.addConstr(cost_regular * x + cost_premium * y <= total_budget, "BudgetConstraint")

    # Add total handbags constraint
    model.addConstr(x + y <= max_total_handbags, "TotalHandbagsConstraint")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum profit
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_handbags()
    if max_profit is not None:
        print(f"Maximum Profit: ${max_profit}")
    else:
        print("No feasible solution found.")