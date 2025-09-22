def optimize_candy_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("CandyProduction")

    # Decision variables: number of peach and cherry packs
    P = m.addVar(vtype=GRB.INTEGER, name="PeachPacks", lb=0)
    C = m.addVar(vtype=GRB.INTEGER, name="CherryPacks", lb=0)

    # Set the objective: minimize total syrup used
    m.setObjective(5 * P + 4 * C, GRB.MINIMIZE)

    # Flavoring constraints
    m.addConstr(P <= 1000, "PeachFlavorLimit")
    m.addConstr(C <= 800, "CherryFlavorLimit")

    # Popularity constraint: peach packs > cherry packs
    # Note: Gurobi does not support strict inequalities directly.
    # To enforce P > C, we can model as P >= C + 1
    m.addConstr(P >= C + 1, "PopularityConstraint")

    # Cherry proportion constraint: C >= (3/7)*P
    # To avoid fractional coefficients, multiply both sides by 7
    m.addConstr(7 * C >= 3 * P, "CherryProportion")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total syrup usage
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_syrup = optimize_candy_production()
    if min_syrup is not None:
        print(f"Minimum Total Syrup Usage: {min_syrup}")
    else:
        print("No feasible solution found.")