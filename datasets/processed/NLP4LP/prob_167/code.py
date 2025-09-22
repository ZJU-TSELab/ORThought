def optimize_transportation():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("TransportationOptimization")

    # Decision variables
    b = m.addVar(vtype=GRB.INTEGER, name="bikes", lb=0)
    c = m.addVar(vtype=GRB.INTEGER, name="cars", lb=0)

    # Set objective: minimize number of bikes
    m.setObjective(b, GRB.MINIMIZE)

    # Add capacity constraint
    m.addConstr(3 * b + 5 * c >= 500, name="capacity_constraint")

    # Add vehicle ratio constraint
    # c <= (2/3) * b
    m.addConstr(c <= (2/3) * b, name="vehicle_ratio_constraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimal number of bikes
        return b.X
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_bikes = optimize_transportation()
    if min_bikes is not None:
        print(f"Minimum number of bikes: {min_bikes}")
    else:
        print("No feasible solution found.")