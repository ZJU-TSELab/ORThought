def optimize_trips():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("TireTransportOptimization")

    # Decision variables
    x = m.addVar(vtype=GRB.INTEGER, name="plane_trips")
    y = m.addVar(vtype=GRB.INTEGER, name="truck_trips")

    # Set objective: minimize total trips
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add constraints
    # Tire delivery constraint
    m.addConstr(10 * x + 6 * y >= 200, name="TireRequirement")
    # Budget constraint
    m.addConstr(1000 * x + 700 * y <= 22000, name="Budget")
    # Trip ratio constraint
    m.addConstr(x <= y, name="TripRatio")
    # Non-negativity is implicit in variable definition

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the total number of trips in the optimal solution
        total_trips = m.objVal
        return total_trips
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_trips = optimize_trips()
    if min_trips is not None:
        print(f"Minimum Total Trips: {min_trips}")
    else:
        print("No feasible solution found.")