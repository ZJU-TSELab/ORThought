def optimize_jar_production(shaping_time=3000, baking_time=4000,
                            profit_thin=5, profit_stubby=9,
                            shaping_time_thin=50, baking_time_thin=90,
                            shaping_time_stubby=30, baking_time_stubby=150):
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Terracotta_Jars_Optimization")
    
    # Decision variables: number of thin and stubby jars
    x = m.addVar(vtype=GRB.INTEGER, name="Thin_Jars")
    y = m.addVar(vtype=GRB.INTEGER, name="Stubby_Jars")
    
    # Set objective: maximize profit
    m.setObjective(profit_thin * x + profit_stubby * y, GRB.MAXIMIZE)
    
    # Add constraints
    m.addConstr(shaping_time_thin * x + shaping_time_stubby * y <= shaping_time, "Shaping_Time")
    m.addConstr(baking_time_thin * x + baking_time_stubby * y <= baking_time, "Baking_Time")
    m.addConstr(x >= 0, "NonNeg_x")
    m.addConstr(y >= 0, "NonNeg_y")
    
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
    max_profit = optimize_jar_production()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")