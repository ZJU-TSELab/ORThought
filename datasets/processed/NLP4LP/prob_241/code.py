def optimize_production_units():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("ProductionUnits")

    # Decision variables
    L = m.addVar(vtype=GRB.INTEGER, name="LargeUnits")
    S = m.addVar(vtype=GRB.INTEGER, name="SmallUnits")

    # Set objective: minimize total parking spots
    m.setObjective(2 * L + S, GRB.MINIMIZE)

    # Add constraints
    # Capacity constraint
    m.addConstr(6 * L + 2 * S >= 80, name="PeopleCapacity")
    # Minimum small units
    m.addConstr(S >= 5, name="MinSmallUnits")
    # Large units at least 75% of total units
    m.addConstr(L >= 3 * S, name="LargeAtLeast75Percent")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimal total parking spots
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_parking_spots = optimize_production_units()
    if min_parking_spots is not None:
        print(f"Minimum Total Parking Spots: {min_parking_spots}")
    else:
        print("No feasible solution found.")