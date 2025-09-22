def optimize_crops():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Crop_Optimization")

    # Decision variables
    # Acres of potatoes
    x = m.addVar(name="Potatoes", lb=0)
    # Acres of cucumbers
    y = m.addVar(name="Cucumbers", lb=0)

    # Set the objective: maximize profit
    profit = 500 * x + 650 * y
    m.setObjective(profit, GRB.MAXIMIZE)

    # Add constraints
    m.addConstr(x + y <= 50, name="Total_land")
    m.addConstr(x >= 12, name="Min_potatoes")
    m.addConstr(y >= 15, name="Min_cucumbers")
    m.addConstr(y <= 2 * x, name="Cucumber_limit")
    m.addConstr(y >= x, name="Preference_cucumbers_more_or_equal_potatoes")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum profit
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage 
if __name__ == "__main__":
    max_profit = optimize_crops()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")