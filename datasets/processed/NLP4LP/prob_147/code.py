def optimize_buses():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("School_Bus_Optimization")
    
    # Decision variables
    x = m.addVar(vtype=GRB.INTEGER, name="small_buses")
    y = m.addVar(vtype=GRB.INTEGER, name="large_buses")
    
    # Set objective: minimize total number of buses
    m.setObjective(x + y, GRB.MINIMIZE)
    
    # Capacity constraint
    m.addConstr(20 * x + 50 * y >= 500, name="capacity_constraint")
    
    # Parking lot constraint (x >= 4y)
    m.addConstr(x - 4 * y >= 0, name="parking_constraint")
    
    # Non-negativity is implicit in variable definition (non-negative by default)
    # but to be explicit:
    m.addConstr(x >= 0, name="x_nonneg")
    m.addConstr(y >= 0, name="y_nonneg")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        total_buses = m.objVal
        return total_buses
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_buses = optimize_buses()
    if min_buses is not None:
        print(f"Minimum Total Buses: {min_buses}")
    else:
        print("No feasible solution found.")