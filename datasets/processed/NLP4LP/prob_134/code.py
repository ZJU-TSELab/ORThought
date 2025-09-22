def optimize_processes():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Process_Optimization")
    
    # Decision variables: hours to run each process
    x1 = m.addVar(name="x1", lb=0)
    x2 = m.addVar(name="x2", lb=0)
    
    # Set the objective: minimize total processing time
    m.setObjective(x1 + x2, GRB.MINIMIZE)
    
    # Add constraints
    
    # Pain killers production constraint
    m.addConstr(35 * x1 + 50 * x2 >= 1200, name="PainKillers")
    
    # Sleeping pills production constraint
    m.addConstr(12 * x1 + 30 * x2 >= 1200, name="SleepingPills")
    
    # Material constraint
    m.addConstr(50 * x1 + 60 * x2 <= 2000, name="Material")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_time = optimize_processes()
    if min_time is not None:
        print(f"Minimum Total Processing Time: {min_time}")
    else:
        print("No feasible solution found.")