def optimize_grilled_cheese():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("GrilledCheeseOptimization")
    
    # Decision variables: number of light and heavy sandwiches
    x = m.addVar(name="light_sandwiches", vtype=GRB.INTEGER, lb=0)
    y = m.addVar(name="heavy_sandwiches", vtype=GRB.INTEGER, lb=0)
    
    # Set the objective: minimize total production time
    m.setObjective(10 * x + 15 * y, GRB.MINIMIZE)
    
    # Add resource constraints
    m.addConstr(2 * x + 3 * y <= 300, name="bread_constraint")
    m.addConstr(3 * x + 5 * y <= 500, name="cheese_constraint")
    
    # Add demand ratio constraint
    m.addConstr(y >= 3 * x, name="heavy_light_ratio")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total production time
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_time = optimize_grilled_cheese()
    if min_time is not None:
        print(f"Minimum Total Production Time: {min_time}")
    else:
        print("No feasible solution found.")