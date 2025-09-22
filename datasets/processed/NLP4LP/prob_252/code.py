def maximize_tests(time_available=7525, min_ear_tests=12, ratio_blood_to_ear=3):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("TestOptimization")

    # Decision variables
    x = model.addVar(name="ear_tests", vtype=GRB.INTEGER, lb=0)
    y = model.addVar(name="blood_tests", vtype=GRB.INTEGER, lb=0)

    # Set objective: maximize total number of tests
    model.setObjective(x + y, GRB.MAXIMIZE)

    # Add constraints
    # Time constraint
    model.addConstr(5 * x + 30 * y <= time_available, name="TimeLimit")
    # Blood to ear ratio constraint
    model.addConstr(y >= ratio_blood_to_ear * x, name="BloodEarRatio")
    # Minimum ear tests
    model.addConstr(x >= min_ear_tests, name="MinEarTests")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum total tests
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_tests = maximize_tests()
    if max_tests is not None:
        print(f"Maximum Tests Performed: {max_tests}")
    else:
        print("No feasible solution found.")