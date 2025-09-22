def optimize_machines():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Machine_Optimization")
    
    # Decision variables
    # Number of machine A (at least 5)
    x_A = m.addVar(vtype=GRB.INTEGER, name="x_A", lb=5)
    # Number of machine B (non-negative)
    x_B = m.addVar(vtype=GRB.INTEGER, name="x_B", lb=0)
    
    # Set objective: minimize total number of machines
    m.setObjective(x_A + x_B, GRB.MINIMIZE)
    
    # Add constraints
    # Production constraint
    m.addConstr(30 * x_A + 50 * x_B >= 1000, "prod_constraint")
    # Electricity constraint
    m.addConstr(100 * x_A + 120 * x_B <= 3000, "energy_constraint")
    # B proportion constraint
    m.addConstr(x_B <= (3/7) * x_A, "b_ratio_constraint")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        total_machines = x_A.X + x_B.X
        return total_machines
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_machines = optimize_machines()
    if min_machines is not None:
        print(f"Minimum Total Number of Machines: {min_machines}")
    else:
        print("No feasible solution found.")