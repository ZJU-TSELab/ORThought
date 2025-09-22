def optimize_sandwich_production(eggs_available=40, bacon_available=70, profit_regular=3, profit_special=4):
    from gurobipy import Model, GRB

    # Create a new model
    model = Model("Sandwich_Optimization")
    
    # Decision variables: number of regular and special sandwiches
    # Both are integers and non-negative
    x = model.addVar(name="Regular", vtype=GRB.INTEGER, lb=0)
    y = model.addVar(name="Special", vtype=GRB.INTEGER, lb=0)
    
    # Set the objective: maximize profit
    model.setObjective(profit_regular * x + profit_special * y, GRB.MAXIMIZE)
    
    # Add constraints
    model.addConstr(2 * x + 3 * y <= eggs_available, "EggsConstraint")
    model.addConstr(3 * x + 5 * y <= bacon_available, "BaconConstraint")
    
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
    max_profit = optimize_sandwich_production()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")