def optimize_transportation():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("TransportationOptimization")

    # Decision variables
    T = m.addVar(vtype=GRB.INTEGER, name="TruckTrips", lb=0, ub=5)
    C = m.addVar(vtype=GRB.INTEGER, name="CarTrips", lb=0)

    # Set objective: minimize total gas consumption
    m.setObjective(20 * T + 15 * C, GRB.MINIMIZE)

    # Add constraints
    # Capacity constraint
    m.addConstr(50 * T + 30 * C >= 500, name="PackageRequirement")
    # Trip ratio constraint
    m.addConstr(C >= (3/7) * T, name="CarTripRatio")
    # T is at most 5 (already set as ub=5)
    # T >= 0 (lb=0), C >= 0 (lb=0)

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total gas consumption
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_gas_consumption = optimize_transportation()
    if min_gas_consumption is not None:
        print(f"Minimum Total Gas Consumption: {min_gas_consumption}")
    else:
        print("No feasible solution found.")