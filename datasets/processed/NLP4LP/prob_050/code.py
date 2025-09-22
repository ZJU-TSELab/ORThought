def optimize_furnaces():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Furnace_Optimization")

    # Decision variables
    x = m.addVar(name="new_furnaces", vtype=GRB.INTEGER, lb=5)  # at least 5 new furnaces
    y = m.addVar(name="old_furnaces", vtype=GRB.INTEGER, lb=0)

    # Set objective: minimize total number of furnaces
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add constraints
    # Heating capacity constraint
    m.addConstr(10 * x + 15 * y >= 200, name="Heating_Capacity")
    # Electricity consumption constraint
    m.addConstr(200 * x + 250 * y <= 3500, name="Electricity")
    # Old model proportion constraint (13 y <= 7 x)
    m.addConstr(13 * y <= 7 * x, name="Old_Model_Proportion")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimal total number of furnaces
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_furnaces = optimize_furnaces()
    if min_furnaces is not None:
        print(f"Minimum Total Number of Furnaces: {min_furnaces}")
    else:
        print("No feasible solution found.")