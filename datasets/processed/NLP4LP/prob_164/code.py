def optimize_volunteers():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("VolunteerOptimization")

    # Decision variables
    S = m.addVar(vtype=GRB.INTEGER, name="Seasonal")
    F = m.addVar(vtype=GRB.INTEGER, name="FullTime")

    # Set objective: maximize total gifts
    m.setObjective(5 * S + 8 * F, GRB.MAXIMIZE)

    # Add constraints
    # Points constraint
    m.addConstr(2 * S + 5 * F <= 200, name="PointsLimit")
    # Seasonal volunteers limit (7S <= 3F)
    m.addConstr(7 * S <= 3 * F, name="SeasonalLimit")
    # Minimum full-time volunteers
    m.addConstr(F >= 10, name="MinFullTime")
    # Non-negativity is implicit in variable definitions

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum total gifts delivered
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_gifts = optimize_volunteers()
    if max_gifts is not None:
        print(f"Maximum Gifts Delivered: {max_gifts}")
    else:
        print("No feasible solution found.")