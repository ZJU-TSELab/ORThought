def optimize_rice_transport():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("RiceTransport")

    # Decision variables
    # Since M = 3L, we only need to define L, and M is derived
    L = m.addVar(vtype=GRB.INTEGER, name="L")
    M = m.addVar(vtype=GRB.INTEGER, name="M")

    # Set the objective: maximize total rice transported
    # Total rice = 30*M + 70*L
    # Since M = 3L, total rice = 90*L + 70*L = 160*L
    m.setObjective(160 * L, GRB.MAXIMIZE)

    # Add constraints
    # M = 3L
    m.addConstr(M == 3 * L, "cart_relation")
    # Horse constraint
    m.addConstr(2 * M + 4 * L <= 60, "horse_limit")
    # Minimum carts
    m.addConstr(L >= 5, "min_large_carts")
    m.addConstr(M >= 5, "min_medium_carts")
    # Link M and L to ensure integrality and consistency
    # (M is defined as 3L, but to ensure M is integer, L must be integer)
    # Already defined as integer, so no extra constraint needed

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Retrieve the value of L
        optimal_L = int(L.X)
        # Compute M
        optimal_M = int(M.X)
        # Compute total rice
        total_rice = 160 * optimal_L
        return total_rice
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_rice = optimize_rice_transport()
    if max_rice is not None:
        print(f"Maximum Total Rice Transported: {max_rice} kg")
    else:
        print("No feasible solution found.")