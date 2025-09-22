def optimize_licenses(sales_limit=300, budget_limit=400000, cost_personal=550, cost_commercial=2000,
                      profit_personal=450, profit_commercial=1200):
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("License_Production_Optimization")
    
    # Decision variables: number of personal and commercial licenses
    x = m.addVar(vtype=GRB.INTEGER, name="Personal_Licenses", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="Commercial_Licenses", lb=0)
    
    # Set the objective: maximize profit
    m.setObjective(profit_personal * x + profit_commercial * y, GRB.MAXIMIZE)
    
    # Add constraints
    m.addConstr(x + y <= sales_limit, "SalesLimit")
    m.addConstr(cost_personal * x + cost_commercial * y <= budget_limit, "BudgetLimit")
    
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
    max_profit = optimize_licenses()
    if max_profit is not None:
        print(f"Maximum Profit: ${max_profit}")
    else:
        print("No feasible solution found.")