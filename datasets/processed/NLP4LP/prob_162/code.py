def optimize_transportation(pollution_van=7, pollution_minibus=10, capacity_van=6, capacity_minibus=10, min_kids=150, max_minibuses=10):
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("SchoolTransportPollutionMinimization")
    
    # Decision variables
    V = m.addVar(vtype=GRB.INTEGER, name="Vans", lb=0)
    M = m.addVar(vtype=GRB.INTEGER, name="Minibuses", lb=0)
    
    # Set objective: minimize total pollution
    m.setObjective(pollution_van * V + pollution_minibus * M, GRB.MINIMIZE)
    
    # Capacity constraint: at least 150 kids transported
    m.addConstr(capacity_van * V + capacity_minibus * M >= min_kids, name="Capacity")
    
    # Max number of minibuses
    m.addConstr(M <= max_minibuses, name="MaxMinibuses")
    
    # Vans must exceed minibuses: V > M
    # Gurobi does not support strict inequalities directly, so we model V >= M + 1
    m.addConstr(V >= M + 1, name="V_greater_than_M")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the total pollution of the optimal solution
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_pollution = optimize_transportation()
    if min_pollution is not None:
        print(f"Minimum Total Pollution: {min_pollution}")
    else:
        print("No feasible solution found.")