def optimize_recycling_bins():
    from gurobipy import Model, GRB

    # Create a new model
    model = Model("RecyclingBins")

    # Decision variables
    # Number of large bins
    L = model.addVar(vtype=GRB.INTEGER, name="LargeBins")
    # Number of small bins
    S = model.addVar(vtype=GRB.INTEGER, name="SmallBins")

    # Set the objective: maximize total recycling units
    # Since S = 3L, we can directly relate the objective to L
    # But for clarity, define the objective as 25*S + 60*L
    model.setObjective(25 * S + 60 * L, GRB.MAXIMIZE)

    # Constraints
    # Relationship between small and large bins
    model.addConstr(S == 3 * L, "SmallLargeRelation")
    # Worker constraint
    model.addConstr(2 * S + 5 * L <= 100, "WorkerLimit")
    # Minimum small bins
    model.addConstr(S >= 10, "MinSmallBins")
    # Minimum large bins
    model.addConstr(L >= 4, "MinLargeBins")
    # Non-negativity is implicit in variable definition

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        total_recycling = model.objVal
        # Retrieve values of decision variables
        small_bins = S.X
        large_bins = L.X
        return total_recycling
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_recycling = optimize_recycling_bins()
    if max_recycling is not None:
        print(f"Maximum Total Recycling Units: {max_recycling}")
    else:
        print("No feasible solution found.")