def optimize_fishing():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("FishingOptimization")

    # Decision variables: acres fished with net (x) and line (y)
    x = m.addVar(name="Net_Acres", lb=0)
    y = m.addVar(name="Line_Acres", lb=0)

    # Set the objective: maximize total fish caught
    m.setObjective(8 * x + 5 * y, GRB.MAXIMIZE)

    # Add constraints
    m.addConstr(x + y <= 250, name="LakeArea")
    m.addConstr(4 * x + 3 * y <= 800, name="Bait")
    m.addConstr(2 * x + y <= 350, name="Pain")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum number of fish caught
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_fish = optimize_fishing()
    if max_fish is not None:
        print(f"Maximum Fish Caught: {max_fish}")
    else:
        print("No feasible solution found.")