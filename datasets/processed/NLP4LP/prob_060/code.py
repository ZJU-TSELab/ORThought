def optimize_washing_machines():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Laundromat Machine Optimization")
    
    # Decision variables: number of machines
    x = m.addVar(vtype=GRB.INTEGER, name="TopLoading")
    y = m.addVar(vtype=GRB.INTEGER, name="FrontLoading")
    
    # Set the objective: minimize total number of machines
    m.setObjective(x + y, GRB.MINIMIZE)
    
    # Add constraints
    # Washing capacity constraint
    m.addConstr(50 * x + 75 * y >= 5000, "WashingCapacity")
    # Energy consumption constraint
    m.addConstr(85 * x + 100 * y <= 7000, "EnergyLimit")
    # Top-loading proportion constraint (transformed to linear form)
    m.addConstr(3 * x <= 2 * y, "TopLoadingProportion")
    # Minimum front-loading machines
    m.addConstr(y >= 10, "MinFrontLoading")
    # Non-negativity is implicit in variable definition
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total number of machines
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_machines = optimize_washing_machines()
    if min_machines is not None:
        print(f"Minimum Total Number of Machines: {min_machines}")
    else:
        print("No feasible solution found.")