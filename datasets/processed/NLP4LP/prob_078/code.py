def optimize_curry_bowls():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("CurryOptimization")
    
    # Decision variables: number of goat and chicken curry bowls
    G = m.addVar(vtype=GRB.INTEGER, name="GoatCurry")
    C = m.addVar(vtype=GRB.INTEGER, name="ChickenCurry")
    
    # Set the objective: minimize total curry base used
    m.setObjective(6 * G + 5 * C, GRB.MINIMIZE)
    
    # Add resource constraints
    m.addConstr(3 * G <= 1500, name="GoatMeatLimit")
    m.addConstr(5 * C <= 2000, name="ChickenMeatLimit")
    
    # Add proportion constraint: C >= 0.25*(G + C) -> 3C >= G
    m.addConstr(3 * C >= G, name="ProportionConstraint")
    
    # Popularity constraint: G > C -> G >= C + 1
    m.addConstr(G >= C + 1, name="PopularityConstraint")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total curry base used
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_curry_base = optimize_curry_bowls()
    if min_curry_base is not None:
        print(f"Minimum Total Curry Base Used: {min_curry_base}")
    else:
        print("No feasible solution found.")