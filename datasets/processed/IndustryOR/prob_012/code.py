def optimize_crop_allocation(total_land=100,
                             profit_c=1500,
                             profit_w=1200,
                             profit_s=1800,
                             profit_so=1600):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Crop_Profit_Maximization")

    # Decision variables
    x_c = model.addVar(name="corn", lb=0)
    x_w = model.addVar(name="wheat", lb=0)
    x_s = model.addVar(name="soybeans", lb=0)
    x_so = model.addVar(name="sorghum", lb=0)

    # Set objective: maximize profit
    model.setObjective(
        profit_c * x_c + profit_w * x_w + profit_s * x_s + profit_so * x_so,
        GRB.MAXIMIZE)

    # Add constraints
    # Total land constraint
    model.addConstr(x_c + x_w + x_s + x_so <= total_land, "TotalLand")
    # Wheat equals three times sorghum
    model.addConstr(x_w == 3 * x_so, "WheatSorghumRatio")
    # Corn at least twice wheat
    model.addConstr(x_c >= 2 * x_w, "CornWheatRatio")
    # Soybeans at least half sorghum
    model.addConstr(x_s >= 0.5 * x_so, "SoySorghumRatio")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the total profit of the optimal solution
        return model.objVal
    else:
        # No feasible solution found
        return None
if __name__ == "__main__":
    result = optimize_crop_allocation()
    if result is not None:
        print(f"Optimal total profit: {result}")
    else:
        print("No feasible solution found.")