def optimize_investment(budget=760000, min_detached=20000, condo_profit_rate=0.5, detached_profit_rate=1.0):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("MrsWatsonInvestment")

    # Decision variables
    x_c = model.addVar(name="CondoInvestment", lb=0)
    x_d = model.addVar(name="DetachedInvestment", lb=min_detached)

    # Set objective: maximize profit
    model.setObjective(condo_profit_rate * x_c + detached_profit_rate * x_d, GRB.MAXIMIZE)

    # Add constraints
    # Total budget constraint
    model.addConstr(x_c + x_d <= budget, name="TotalBudget")
    # Minimum condo investment (20% of total)
    # Rearranged as: 0.80 * x_c - 0.20 * x_d >= 0
    model.addConstr(0.80 * x_c - 0.20 * x_d >= 0, name="MinCondoPercent")
    # Minimum investment in detached houses
    model.addConstr(x_d >= min_detached, name="MinDetached")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum profit
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_investment()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")