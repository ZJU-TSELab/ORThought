def optimize_swabs(time_limit=20000, min_nasal=30, ratio=4):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Swab Optimization")
    
    # Decision variables: number of throat and nasal swabs
    T = model.addVar(name="ThroatSwabs", vtype=GRB.INTEGER, lb=0)
    N = model.addVar(name="NasalSwabs", vtype=GRB.INTEGER, lb=0)
    
    # Set the objective: maximize total number of patients (swabs)
    model.setObjective(T + N, GRB.MAXIMIZE)
    
    # Add constraints
    # Time constraint
    model.addConstr(5 * T + 3 * N <= time_limit, name="TimeLimit")
    # Minimum nasal swabs
    model.addConstr(N >= min_nasal, name="MinNasal")
    # Throat to nasal ratio
    model.addConstr(T >= ratio * N, name="ThroatNasalRatio")
    
    # Optimize the model
    model.optimize()
    
    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum total number of patients served
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_patients = optimize_swabs()
    if max_patients is not None:
        print(f"Maximum Number of Patients Served: {max_patients}")
    else:
        print("No feasible solution found.")