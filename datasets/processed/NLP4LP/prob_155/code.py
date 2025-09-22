def minimize_planes():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("MinimizePlanes")

    # Decision variables: number of large and small planes
    L = m.addVar(vtype=GRB.INTEGER, name="LargePlanes", lb=0)
    S = m.addVar(vtype=GRB.INTEGER, name="SmallPlanes", lb=0)

    # Set the objective: minimize total number of planes
    m.setObjective(L + S, GRB.MINIMIZE)

    # Capacity constraint: at least 300 cars delivered
    m.addConstr(30 * L + 10 * S >= 300, name="CapacityConstraint")

    # Relationship constraint: large planes less than small planes
    m.addConstr(L <= S - 1, name="PlaneCountConstraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimum total number of planes
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_planes = minimize_planes()
    if min_planes is not None:
        print(f"Minimum Total Planes: {min_planes}")
    else:
        print("No feasible solution found.")