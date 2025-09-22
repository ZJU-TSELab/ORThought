def optimize_bakery_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("BakeryProduction")

    # Decision variables: number of brownies and lemon squares
    B = m.addVar(name="Brownies", vtype=GRB.INTEGER, lb=0)
    L = m.addVar(name="LemonSquares", vtype=GRB.INTEGER, lb=0)

    # Set the objective: minimize total fiber
    m.setObjective(4 * B + 6 * L, GRB.MINIMIZE)

    # Add resource constraints
    m.addConstr(5 * B <= 2500, name="ChocolateConstraint")
    m.addConstr(7 * L <= 3300, name="LemonConstraint")

    # Lemon squares must be more than brownies
    # Note: Gurobi does not support strict inequalities directly.
    # To model L > B, we can use L >= B + 1
    m.addConstr(L >= B + 1, name="L_greater_than_B")

    # At least 40% of total items are brownies
    # The original constraint: 3B >= 2L
    m.addConstr(3 * B >= 2 * L, name="BrowniePercentage")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimal fiber usage
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_fiber = optimize_bakery_production()
    if min_fiber is not None:
        print(f"Minimum Total Fiber Usage: {min_fiber}")
    else:
        print("No feasible solution found.")