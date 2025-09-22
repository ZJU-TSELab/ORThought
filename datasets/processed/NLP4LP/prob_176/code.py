def optimize_corn_transport(
    min_boxes=500,
    ferry_capacity=20,
    rail_capacity=15,
    min_ratio=4
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Farmer_Corn_Transport")

    # Decision variables: number of ferry trips and light rail trips
    F = model.addVar(vtype=GRB.INTEGER, name="FerryTrips", lb=0)
    L = model.addVar(vtype=GRB.INTEGER, name="RailTrips", lb=0)

    # Set the objective: minimize total trips
    model.setObjective(F + L, GRB.MINIMIZE)

    # Add constraints
    # Capacity constraint: total boxes >= min_boxes
    model.addConstr(20 * F + 15 * L >= min_boxes, name="TotalBoxes")
    # Trip ratio constraint: L >= 4 * F
    model.addConstr(L >= min_ratio * F, name="TripRatio")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        total_trips = F.X + L.X
        return total_trips
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_transport = optimize_corn_transport()
    if min_transport is not None:
        print(f"Minimum Total Transport (Ferry + Rail): {min_transport}")
    else:
        print("No feasible solution found.")