def optimize_bakery_profit(
    profit_strawberry=5.5,
    profit_sugar=12,
    max_demand_strawberry=100,
    max_demand_sugar=80,
    max_total_production=100
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Bakery_Optimization")

    # Decision variables
    x1 = model.addVar(name="x1", lb=0)  # Strawberry cookies
    x2 = model.addVar(name="x2", lb=0)  # Sugar cookies

    # Set objective: maximize profit
    model.setObjective(profit_strawberry * x1 + profit_sugar * x2, GRB.MAXIMIZE)

    # Add constraints
    model.addConstr(x1 <= max_demand_strawberry, name="Demand_Strawberry")
    model.addConstr(x2 <= max_demand_sugar, name="Demand_Sugar")
    model.addConstr(x1 + x2 <= max_total_production, name="Total_Production")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_bakery_profit()
    if max_profit is not None:
        print(f"Maximum Profit: ${max_profit:.2f}")
    else:
        print("No feasible solution found.")