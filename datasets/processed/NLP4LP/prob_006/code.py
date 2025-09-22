def optimize_furniture_production(
    profit_chair=43,
    profit_dresser=52,
    stain_available=17,
    oak_available=11,
    stain_per_chair=1.4,
    stain_per_dresser=1.1,
    oak_per_chair=2,
    oak_per_dresser=3
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Furniture_Production_MaxProfit")

    # Decision variables: number of chairs and dressers
    x = model.addVar(name="chairs", lb=0, vtype=GRB.INTEGER)
    y = model.addVar(name="dressers", lb=0, vtype=GRB.INTEGER)

    # Set the objective: maximize profit
    model.setObjective(profit_chair * x + profit_dresser * y, GRB.MAXIMIZE)

    # Add resource constraints
    model.addConstr(stain_per_chair * x + stain_per_dresser * y <= stain_available, "stain_constraint")
    model.addConstr(oak_per_chair * x + oak_per_dresser * y <= oak_available, "oak_constraint")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum profit
        return model.objVal
    else:
        # No feasible solution found
        return None

print(optimize_furniture_production())