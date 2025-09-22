def optimize_art_production(
    paint_available=100,
    glitter_available=50,
    glue_available=70,
    min_large=5,
    min_small=5,
    profit_large=30,
    profit_small=15
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Art_Production_Maximize_Profit")

    # Decision variables: number of large and small art pieces
    x = model.addVar(vtype=GRB.INTEGER, name="Large_Art", lb=min_large)
    y = model.addVar(vtype=GRB.INTEGER, name="Small_Art", lb=min_small)

    # Set the objective: maximize profit
    model.setObjective(profit_large * x + profit_small * y, GRB.MAXIMIZE)

    # Add material constraints
    model.addConstr(4 * x + 2 * y <= paint_available, "Paint_Constraint")
    model.addConstr(3 * x + y <= glitter_available, "Glitter_Constraint")
    model.addConstr(5 * x + 2 * y <= glue_available, "Glue_Constraint")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum profit
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_art_production()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")