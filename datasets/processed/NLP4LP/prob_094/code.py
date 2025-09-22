def optimize_chemical_usage():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Chemical_Optimization")

    # Decision variables
    # x: units of cleansing chemical
    # y: units of odor-removing chemical
    x = m.addVar(name="x", lb=0)
    y = m.addVar(name="y", lb=0)

    # Set the objective: minimize total cleaning time
    m.setObjective(4 * x + 6 * y, GRB.MINIMIZE)

    # Add constraints
    m.addConstr(x >= 100, name="min_cleansing")
    m.addConstr(x + y <= 300, name="total_chemicals")
    m.addConstr(x <= 2 * y, name="strength_ratio")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total time
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_time = optimize_chemical_usage()
    if min_time is not None:
        print(f"Minimum Total Cleaning Time: {min_time}")
    else:
        print("No feasible solution found.")