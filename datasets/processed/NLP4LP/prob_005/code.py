def optimize_ad_campaign(
    budget=10000,
    max_soorchle=15,
    min_z_ratio=0.05,
    max_wassa_ratio=1/3
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Advertising_Optimization")

    # Decision variables: number of ads for each media type
    x_z = model.addVar(vtype=GRB.INTEGER, name="z_tube")
    x_s = model.addVar(vtype=GRB.INTEGER, name="soorchle")
    x_w = model.addVar(vtype=GRB.INTEGER, name="wassa")

    # Set objective: maximize total viewers
    model.setObjective(
        400000 * x_z + 5000 * x_s + 3000 * x_w,
        GRB.MAXIMIZE
    )

    # Add constraints
    # Budget constraint
    model.addConstr(1000 * x_z + 200 * x_s + 100 * x_w <= budget, "Budget")
    # Soorchle limit
    model.addConstr(x_s <= max_soorchle, "SoorchleLimit")
    # Wassa at most a third of total ads
    model.addConstr(2 * x_w <= x_z + x_s, "WassaRatio")
    # Z-tube at least 5% of total ads
    # 19 * x_z >= x_s + x_w
    model.addConstr(19 * x_z >= x_s + x_w, "ZMinRatio")
    # Non-negativity is implicit in variable definition

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        total_viewers = model.objVal
        return total_viewers
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_viewers = optimize_ad_campaign()
    if max_viewers is not None:
        print(f"Maximum Total Viewers: {max_viewers}")
    else:
        print("No feasible solution found.")