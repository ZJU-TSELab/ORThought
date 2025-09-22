def optimize_pills():
    from gurobipy import Model, GRB, quicksum

    # Create a new model
    m = Model("PillProduction")

    # Decision variables
    # L: number of large pills (integer, at least 100)
    L = m.addVar(vtype=GRB.INTEGER, name="LargePills", lb=100)
    # S: number of small pills (integer, at least 0)
    S = m.addVar(vtype=GRB.INTEGER, name="SmallPills", lb=0)

    # Set objective: minimize total filler used
    m.setObjective(2 * L + S, GRB.MINIMIZE)

    # Add resource constraint for medicinal ingredients
    m.addConstr(3 * L + 2 * S <= 1000, "MedicinalConstraint")

    # Add constraint for small pills being at least 60% of total
    # S >= 1.5 * L
    m.addConstr(S >= 1.5 * L, "SmallPercentageConstraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimal filler usage
        return m.objVal
    else:
        # No feasible solution
        return None

# Example usage
if __name__ == "__main__":
    min_filler = optimize_pills()
    if min_filler is not None:
        print(f"Minimum Total Filler Used: {min_filler}")
    else:
        print("No feasible solution found.")