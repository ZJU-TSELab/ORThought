def optimize_tests(time_available=8000, min_swabs=20):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("VirusTestingOptimization")

    # Decision variables
    x = model.addVar(name="spit_tests", vtype=GRB.INTEGER, lb=0)
    y = model.addVar(name="swab_tests", vtype=GRB.INTEGER, lb=0)

    # Set objective: maximize total tests
    model.setObjective(x + y, GRB.MAXIMIZE)

    # Add constraints
    # Time constraint
    model.addConstr(10 * x + 15 * y <= time_available, name="TimeLimit")
    # Ratio constraint: spit tests at least twice swabs
    model.addConstr(x >= 2 * y, name="Ratio")
    # Minimum swabs
    model.addConstr(y >= min_swabs, name="MinSwabs")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        total_tests = model.objVal
        return total_tests
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_tests = optimize_tests()
    if max_tests is not None:
        print(f"Maximum Total Tests: {max_tests}")
    else:
        print("No feasible solution found.")