def optimize_cavity_filling():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("dentist_cavity_filling")
    
    # Decision variables: number of molars and canines to fill
    x_m = m.addVar(vtype=GRB.INTEGER, name="molars")
    x_c = m.addVar(vtype=GRB.INTEGER, name="canines")
    
    # Set the objective: minimize total pain killer
    m.setObjective(3 * x_m + 2.3 * x_c, GRB.MINIMIZE)
    
    # Add constraints
    # Resin constraint
    m.addConstr(20 * x_m + 15 * x_c <= 3000, "resin_limit")
    
    # Canine proportion constraint: x_c >= 1.5 * x_m
    m.addConstr(x_c >= 1.5 * x_m, "canine_proportion")
    
    # Minimum molars filled
    m.addConstr(x_m >= 45, "min_molars")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimal pain killer usage
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_pain_killer = optimize_cavity_filling()
    if min_pain_killer is not None:
        print(f"Minimum Total Pain Killer Usage: {min_pain_killer}")
    else:
        print("No feasible solution found.")