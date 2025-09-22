def optimize_transportation():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("TransportationOptimization")

    # Decision variables: number of trains and trams
    T = m.addVar(name="Trains", vtype=GRB.INTEGER, lb=0)
    M = m.addVar(name="Trams", vtype=GRB.INTEGER, lb=0)

    # Set the objective: minimize total units
    m.setObjective(T + M, GRB.MINIMIZE)

    # Capacity constraint
    m.addConstr(120 * T + 30 * M >= 600, name="CapacityConstraint")

    # Relationship constraint
    m.addConstr(M >= 2 * T, name="TramTrainRelation")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total number of units
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_units = optimize_transportation()
    if min_units is not None:
        print(f"Minimum Total Units (Trains + Trams): {min_units}")
    else:
        print("No feasible solution found.")