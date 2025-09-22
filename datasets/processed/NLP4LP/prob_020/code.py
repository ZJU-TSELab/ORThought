def optimize_desktops(sales_limit=200, budget_limit=300000, premium_cost=2000, regular_cost=1000,
                      premium_profit=500, regular_profit=300):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Desktop_Production_Optimization")

    # Decision variables: number of premium and regular desktops
    x = model.addVar(vtype=GRB.INTEGER, name="Premium_Desktops", lb=0)
    y = model.addVar(vtype=GRB.INTEGER, name="Regular_Desktops", lb=0)

    # Set objective: maximize profit
    model.setObjective(premium_profit * x + regular_profit * y, GRB.MAXIMIZE)

    # Add constraints
    model.addConstr(x + y <= sales_limit, "Sales_Limit")
    model.addConstr(premium_cost * x + regular_cost * y <= budget_limit, "Budget_Limit")

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
    max_profit = optimize_desktops()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")