def optimize_tests():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("DiseaseTestingOptimization")
    
    # Decision variables
    T = m.addVar(name="TemperatureChecks", vtype=GRB.INTEGER, lb=0)
    B = m.addVar(name="BloodTests", vtype=GRB.INTEGER, lb=0)
    
    # Set the objective: maximize total tests
    m.setObjective(T + B, GRB.MAXIMIZE)
    
    # Add constraints
    m.addConstr(B >= 45, name="MinBloodTests")
    m.addConstr(T >= 5 * B, name="TempCheckRatio")
    m.addConstr(2 * T + 10 * B <= 22000, name="StaffMinutes")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum number of tests performed
        return m.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_tests = optimize_tests()
    if max_tests is not None:
        print(f"Maximum Tests Performed: {max_tests}")
    else:
        print("No feasible solution found.")