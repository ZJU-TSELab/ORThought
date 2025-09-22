def optimize_ski_lifts():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("SkiLiftsOptimization")
    
    # Decision variables
    # x: number of densely-seated lifts
    # y: number of loosely-seated lifts
    x = m.addVar(vtype=GRB.INTEGER, name="x", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="y", lb=5)
    
    # Set the objective: minimize total number of lifts
    m.setObjective(x + y, GRB.MINIMIZE)
    
    # Capacity constraint
    m.addConstr(45 * x + 20 * y >= 1000, name="capacity")
    
    # Electricity constraint
    m.addConstr(30 * x + 22 * y <= 940, name="electricity")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total number of lifts
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_lifts = optimize_ski_lifts()
    if min_lifts is not None:
        print(f"Minimum Total Lifts: {min_lifts}")
    else:
        print("No feasible solution found.")