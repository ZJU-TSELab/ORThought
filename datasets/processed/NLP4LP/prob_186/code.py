def optimize_boats():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("FishingBoatsOptimization")

    # Decision variables
    # x: number of canoes
    # y: number of diesel boats
    x = m.addVar(vtype=GRB.INTEGER, name="canoes", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="diesel_boats", lb=0)

    # Set objective: minimize total number of boats
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add constraints
    # Fish transportation constraint
    m.addConstr(10 * x + 15 * y >= 1000, name="fish_transport")
    # Environmental constraint
    m.addConstr(x >= 3 * y, name="env_rule")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimal total number of boats
        return m.objVal
    else:
        # No feasible solution
        return None

# Example usage
if __name__ == "__main__":
    min_boats = optimize_boats()
    if min_boats is not None:
        print(f"Minimum Total Boats: {min_boats}")
    else:
        print("No feasible solution found.")