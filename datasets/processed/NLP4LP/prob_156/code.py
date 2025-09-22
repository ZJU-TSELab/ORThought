def optimize_wagons():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("WagonOptimization")

    # Decision variables
    # x: number of small wagons
    # y: number of large wagons
    x = m.addVar(name="small_wagons", vtype=GRB.INTEGER, lb=0)
    y = m.addVar(name="large_wagons", vtype=GRB.INTEGER, lb=0)

    # Set objective: minimize total wagons
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add constraints
    # Ore transportation constraint
    m.addConstr(20 * x + 50 * y >= 2000, name="OreRequirement")
    # Small wagons at least twice large wagons
    m.addConstr(x >= 2 * y, name="SmallLargeRatio")
    # Minimum large wagons
    m.addConstr(y >= 10, name="MinLargeWagons")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        total_wagons = m.objVal
        return total_wagons
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_wagons = optimize_wagons()
    if min_wagons is not None:
        print(f"Minimum Total Wagons: {min_wagons}")
    else:
        print("No feasible solution found.")