def optimize_diet(max_magnesium=200, min_pills=10, ratio_gummies_to_pills=3):
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Magnesium_Zinc_Optimization")
    
    # Decision variables: number of gummies and pills
    x = m.addVar(name="Gummies", lb=0, vtype=GRB.INTEGER)
    y = m.addVar(name="Pills", lb=0, vtype=GRB.INTEGER)
    
    # Set the objective: maximize zinc intake
    m.setObjective(4 * x + 5 * y, GRB.MAXIMIZE)
    
    # Add constraints
    m.addConstr(y >= min_pills, "MinPills")
    m.addConstr(x >= ratio_gummies_to_pills * y, "GummiesPillsRatio")
    m.addConstr(3 * x + 2 * y <= max_magnesium, "MagnesiumLimit")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum zinc intake
        return m.objVal
    else:
        # No feasible solution
        return None

# Example usage
print(optimize_diet())