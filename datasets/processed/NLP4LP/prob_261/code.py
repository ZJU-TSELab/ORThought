def optimize_medication_batches():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Hospital_Medication_Production")
    
    # Decision variables: number of batches of medication patches and anti-biotic creams
    x = m.addVar(vtype=GRB.INTEGER, name="Medication_Patches")
    y = m.addVar(vtype=GRB.INTEGER, name="AntiBiotic_Creams")
    
    # Set the objective: maximize total number of people treated
    m.setObjective(3 * x + 2 * y, GRB.MAXIMIZE)
    
    # Add constraints
    m.addConstr(3 * x + 5 * y <= 400, "Time_Constraint")
    m.addConstr(5 * x + 6 * y <= 530, "Material_Constraint")
    m.addConstr(x + y <= 100, "Batch_Limit")
    m.addConstr(y >= 2 * x, "Creams_at_least_twice_patches")
    m.addConstr(x >= 0, "NonNeg_x")
    m.addConstr(y >= 0, "NonNeg_y")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum number of people treated
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_people_treated = optimize_medication_batches()
    if max_people_treated is not None:
        print(f"Maximum People Treated: {max_people_treated}")
    else:
        print("No feasible solution found.")