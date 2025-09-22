def optimize_cake_production(
    batter_available=20000,
    milk_available=14000,
    profit_crepe=12,
    profit_sponge=10,
    profit_birthday=15,
    batter_crepe=400,
    milk_crepe=200,
    batter_sponge=500,
    milk_sponge=300,
    batter_birthday=450,
    milk_birthday=350
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Cake_Production_Maximize_Profit")

    # Decision variables: number of each cake type (integer, >= 0)
    x1 = model.addVar(vtype=GRB.INTEGER, name="Crepe", lb=0)
    x2 = model.addVar(vtype=GRB.INTEGER, name="Sponge", lb=0)
    x3 = model.addVar(vtype=GRB.INTEGER, name="Birthday", lb=0)

    # Set objective: maximize total profit
    model.setObjective(
        profit_crepe * x1 + profit_sponge * x2 + profit_birthday * x3,
        GRB.MAXIMIZE
    )

    # Add resource constraints
    model.addConstr(
        batter_crepe * x1 + batter_sponge * x2 + batter_birthday * x3 <= batter_available,
        name="BatterConstraint"
    )
    model.addConstr(
        milk_crepe * x1 + milk_sponge * x2 + milk_birthday * x3 <= milk_available,
        name="MilkConstraint"
    )

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal profit
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_cake_production()
    if max_profit is not None:
        print(f"Maximum Profit: ${max_profit}")
    else:
        print("No feasible solution found.")