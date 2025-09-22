def optimize_glass_production(
    max_time=300,
    profit_regular=8,
    profit_tempered=10,
    heating_time_regular=3,
    cooling_time_regular=5,
    heating_time_tempered=5,
    cooling_time_tempered=8
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("GlassProductionMaxProfit")

    # Decision variables: number of regular and tempered panes
    x = model.addVar(vtype=GRB.INTEGER, name="Regular")
    y = model.addVar(vtype=GRB.INTEGER, name="Tempered")

    # Set objective: maximize profit
    model.setObjective(profit_regular * x + profit_tempered * y, GRB.MAXIMIZE)

    # Add constraints
    # Heating machine constraint
    model.addConstr(heating_time_regular * x + heating_time_tempered * y <= max_time, "HeatingTime")
    # Cooling machine constraint
    model.addConstr(cooling_time_regular * x + cooling_time_tempered * y <= max_time, "CoolingTime")
    # Non-negativity constraints are implicit with variable types

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
    max_profit = optimize_glass_production()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")