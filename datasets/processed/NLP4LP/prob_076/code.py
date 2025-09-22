def optimize_slicers():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Slicer_Optimization")
    
    # Decision variables: number of manual and automatic slicers
    x = m.addVar(vtype=GRB.INTEGER, name="manual_slicers", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="automatic_slicers", lb=0)
    
    # Set the objective: minimize total number of slicers
    m.setObjective(x + y, GRB.MINIMIZE)
    
    # Add constraints
    # Slicing capacity constraint
    m.addConstr(5 * x + 8 * y >= 50, name="slicing_capacity")
    # Grease constraint
    m.addConstr(3 * x + 6 * y <= 35, name="grease_limit")
    # Operational constraint: manual slicers less than automatic slicers
    m.addConstr(x <= y - 1, name="manual_less_than_auto")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimal total number of slicers
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_slicers = optimize_slicers()
    if min_slicers is not None:
        print(f"Minimum Total Number of Slicers: {min_slicers}")
    else:
        print("No feasible solution found.")