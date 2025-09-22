def optimize_dairy_production(milk_barrels=50,
                              max_hours=480,
                              max_A1=100,
                              profit_A1=24,
                              profit_A2=16):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Dairy_Production_Maximization")

    # Decision variables
    x_A = model.addVar(name="A1_kg", lb=0, vtype=GRB.CONTINUOUS)
    x_B = model.addVar(name="A2_kg", lb=0, vtype=GRB.CONTINUOUS)

    # Set objective: maximize profit
    model.setObjective(profit_A1 * x_A + profit_A2 * x_B, GRB.MAXIMIZE)

    # Constraints

    # Milk supply constraint
    # (x_A / 3) + (x_B / 4) <= total barrels
    model.addConstr((x_A / 3) + (x_B / 4) <= milk_barrels, name="MilkSupply")

    # Processing time constraint
    # 4 * x_A + 2 * x_B <= total hours
    model.addConstr(4 * x_A + 2 * x_B <= max_hours, name="ProcessingTime")

    # Capacity constraint for A1
    model.addConstr(x_A <= max_A1, name="A1Capacity")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
if __name__ == "__main__":  # pragma: no cover
    result = optimize_dairy_production()
    if result is not None:
        print(f"Optimal profit: {result}")
    else:
        print("No feasible solution found.")