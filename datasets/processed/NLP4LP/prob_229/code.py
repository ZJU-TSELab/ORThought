def optimize_pills(budget=10000, cost_prevention=15, cost_treatment=25, min_treatment=50):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Hospital_Pills_Optimization")
    
    # Decision variables
    T = model.addVar(name="Treatment_Pills", vtype=GRB.INTEGER, lb=min_treatment)
    P = model.addVar(name="Prevention_Pills", vtype=GRB.INTEGER, lb=0)
    
    # Set objective: maximize number of treatment pills (patients)
    model.setObjective(T, GRB.MAXIMIZE)
    
    # Add constraints
    # Budget constraint
    model.addConstr(cost_prevention * P + cost_treatment * T <= budget, name="Budget")
    # Prevention pills at least twice treatment pills
    model.addConstr(P >= 2 * T, name="Prevention_vs_Treatment")
    
    # Optimize the model
    model.optimize()
    
    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum number of patients (treatment pills)
        return int(T.X)
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_patients = optimize_pills()
    if max_patients is not None:
        print(f"Maximum Patients Treated: {max_patients}")
    else:
        print("No feasible solution found.")