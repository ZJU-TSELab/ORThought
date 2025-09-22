def optimize_toy_store(
    max_budget=700,
    min_plush=90,
    max_plush=190,
    plush_cost=3,
    doll_cost=2,
    plush_profit=4,
    doll_profit=2
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("ToyStoreProfitMaximization")

    # Decision variables
    x = model.addVar(vtype=GRB.INTEGER, name="PlushToys")
    y = model.addVar(vtype=GRB.INTEGER, name="Dolls")

    # Set objective: maximize profit
    model.setObjective(plush_profit * x + doll_profit * y, GRB.MAXIMIZE)

    # Add constraints
    # Budget constraint
    model.addConstr(plush_cost * x + doll_cost * y <= max_budget, "BudgetLimit")
    # Plush toy sales bounds
    model.addConstr(x >= min_plush, "MinPlush")
    model.addConstr(x <= max_plush, "MaxPlush")
    # Dolls sold constraint
    model.addConstr(y <= 2 * x, "DollsLimit")
    # Non-negativity is implicit in variable definition

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
    max_profit = optimize_toy_store()
    if max_profit is not None:
        print(f"Maximum Profit: ${max_profit}")
    else:
        print("No feasible solution found.")