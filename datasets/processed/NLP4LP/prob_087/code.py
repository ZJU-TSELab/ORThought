def optimize_bottle_production(
    total_vine_ml=100000,
    vintage_volume_ml=500,
    regular_volume_ml=750,
    min_vintage_bottles=10,
    ratio_regular_to_vintage=4
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Vine_Bottles_Production")

    # Decision variables: number of vintage and regular bottles
    V = model.addVar(vtype=GRB.INTEGER, name="Vintage", lb=min_vintage_bottles)
    R = model.addVar(vtype=GRB.INTEGER, name="Regular", lb=0)

    # Set the objective: maximize total number of bottles
    model.setObjective(V + R, GRB.MAXIMIZE)

    # Add volume constraint
    model.addConstr(
        vintage_volume_ml * V + regular_volume_ml * R <= total_vine_ml,
        name="VolumeConstraint"
    )

    # Add ratio constraint: R >= 4V
    model.addConstr(
        R >= ratio_regular_to_vintage * V,
        name="RatioConstraint"
    )

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        total_bottles = V.X + R.X
        return total_bottles
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_bottles = optimize_bottle_production()
    if max_bottles is not None:
        print(f"Maximum Total Number of Bottles: {max_bottles}")
    else:
        print("No feasible solution found.")