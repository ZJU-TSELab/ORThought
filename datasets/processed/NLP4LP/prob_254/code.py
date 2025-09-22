def optimize_carts():
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Golf_Carts_Optimization")

    # Decision variables: number of golf carts (G) and pull carts (P)
    G = model.addVar(vtype=GRB.INTEGER, name="GolfCarts", lb=0)
    P = model.addVar(vtype=GRB.INTEGER, name="PullCarts", lb=0)

    # Set the objective: minimize total carts
    model.setObjective(G + P, GRB.MINIMIZE)

    # Add constraints
    # Guest transportation constraint
    model.addConstr(4 * G + P >= 80, name="GuestTransport")
    # Cart composition ratio constraint
    model.addConstr(2 * G <= 3 * P, name="CartRatio")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal total number of carts
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_carts = optimize_carts()
    if min_carts is not None:
        print(f"Minimum Total Carts (Golf + Pull): {min_carts}")
    else:
        print("No feasible solution found.")