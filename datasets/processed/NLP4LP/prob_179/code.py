def optimize_grape_transport(
    max_small_crates=100,
    max_large_crates=50,
    min_large_crates=10,
    max_total_crates=60,
    small_crate_capacity=200,
    large_crate_capacity=500
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("GrapeTransport")

    # Decision variables
    x = model.addVar(vtype=GRB.INTEGER, name="small_crates")
    y = model.addVar(vtype=GRB.INTEGER, name="large_crates")

    # Set objective: maximize total grapes
    model.setObjective(
        small_crate_capacity * x + large_crate_capacity * y,
        GRB.MAXIMIZE
    )

    # Add constraints
    model.addConstr(x >= 3 * y, name="small_crate_pref")
    model.addConstr(x <= max_small_crates, name="max_small_crates")
    model.addConstr(y <= max_large_crates, name="max_large_crates")
    model.addConstr(x + y <= max_total_crates, name="truck_capacity")
    model.addConstr(y >= min_large_crates, name="min_large_crates")
    model.addConstr(x >= 0, name="nonneg_small")
    model.addConstr(y >= 0, name="nonneg_large")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum total grapes transported
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_grapes = optimize_grape_transport()
    if max_grapes is not None:
        print(f"Maximum Total Grapes Transported: {max_grapes}")
    else:
        print("No feasible solution found.")