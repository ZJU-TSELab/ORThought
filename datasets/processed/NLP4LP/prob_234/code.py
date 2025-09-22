def optimize_cruise_trips():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("CruiseOptimization")

    # Decision variables
    L = m.addVar(vtype=GRB.INTEGER, name="LargeTrips", lb=0)
    S = m.addVar(vtype=GRB.INTEGER, name="SmallTrips", lb=0)

    # Set objective: minimize total pollution
    m.setObjective(20 * L + 15 * S, GRB.MINIMIZE)

    # Add constraints
    m.addConstr(L <= 7, "MaxLargeTrips")
    m.addConstr(2000 * L + 800 * S >= 20000, "CustomerCapacity")
    m.addConstr(S >= (2/3) * L, "SmallShipProportion")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the total pollution (objective value)
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_pollution = optimize_cruise_trips()
    if min_pollution is not None:
        print(f"Minimum Total Pollution: {min_pollution} units")
    else:
        print("No feasible solution found.")