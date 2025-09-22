def optimize_bakery_profit(oven_hours=70, pastry_hours=32,
                           profit_bagels=20, profit_croissants=40,
                           max_bagels=None, max_croissants=None):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("BakeryOptimization")
    
    # Decision variables: number of batches of bagels and croissants
    x = model.addVar(name="Bagels")
    y = model.addVar(name="Croissants")
    
    # Set the objective: maximize profit
    model.setObjective(profit_bagels * x + profit_croissants * y, GRB.MAXIMIZE)
    
    # Add oven time constraint
    model.addConstr(2 * x + y <= oven_hours, "OvenTime")
    
    # Add pastry chef time constraint
    model.addConstr(0.25 * x + 2 * y <= pastry_hours, "PastryTime")
    
    # Optional: add upper bounds if specified
    if max_bagels is not None:
        model.addConstr(x <= max_bagels, "MaxBagels")
    if max_croissants is not None:
        model.addConstr(y <= max_croissants, "MaxCroissants")
    
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
    max_profit = optimize_bakery_profit()
    if max_profit is not None:
        print(f"Maximum profit from bakery operations: ${max_profit:.2f}")
    else:
        print("No feasible solution found.")