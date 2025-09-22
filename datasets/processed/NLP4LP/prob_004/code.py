def optimize_staffing(wage_budget=30000, min_total_workers=50, min_young=10):
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Store Staffing Optimization")
    
    # Decision variables: number of senior citizens and young adults
    S = m.addVar(name="SeniorCitizens", lb=0, vtype=GRB.INTEGER)
    Y = m.addVar(name="YoungAdults", lb=0, vtype=GRB.INTEGER)
    
    # Set the objective: minimize total wages
    m.setObjective(500 * S + 750 * Y, GRB.MINIMIZE)
    
    # Add constraints
    # Wage budget constraint
    m.addConstr(500 * S + 750 * Y <= wage_budget, "WageBudget")
    # Total workers per week
    m.addConstr(S + Y >= min_total_workers, "MinTotalWorkers")
    # Minimum young adults
    m.addConstr(Y >= min_young, "MinYoungAdults")
    # Young adults at least a third of senior citizens
    m.addConstr(3 * Y >= S, "YoungAtLeastOneThirdSenior")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    total_wages = optimize_staffing()
    if total_wages is not None:
        print(f"Minimum Total Wages: {total_wages}")
    else:
        print("No feasible solution found.")