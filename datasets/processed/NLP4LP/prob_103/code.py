def optimize_baby_food():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("BabyFoodOptimization")
    
    # Decision variables
    # Since servings are discrete, define as integer variables
    C = m.addVar(name="C", lb=2)  # Carrot servings, at least 2
    A = m.addVar(name="A", lb=0)        # Apple servings
    
    # Add the preference constraint: A = 3 * C
    m.addConstr(A == 3 * C, name="preference")
    
    # Add the folate constraint: 5A + 3C <= 100
    m.addConstr(5 * A + 3 * C <= 100, name="folate_limit")
    
    # Objective: maximize total fat intake = 2A + 4C
    m.setObjective(2 * A + 4 * C, GRB.MAXIMIZE)
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum fat intake
        return m.objVal
    else:
        # No feasible solution
        return None

# Example usage
print(optimize_baby_food())