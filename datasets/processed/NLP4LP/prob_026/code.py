def optimize_food_truck_profit(
    max_budget=20000,
    min_mangos=100,
    max_mangos=150,
    mango_cost=5,
    guava_cost=3,
    mango_profit=3,
    guava_profit=4
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("FoodTruckOptimization")

    # Decision variables
    x = model.addVar(vtype=GRB.INTEGER, lb=min_mangos, ub=max_mangos, name="mangos")
    y = model.addVar(vtype=GRB.INTEGER, lb=0, name="guavas")

    # Set objective: maximize profit
    model.setObjective(mango_profit * x + guava_profit * y, GRB.MAXIMIZE)

    # Add constraints
    # Budget constraint
    model.addConstr(mango_cost * x + guava_cost * y <= max_budget, "budget")
    # Guava sales relative to mangos
    model.addConstr(y <= (1/3) * x, "guava_mango_ratio")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum profit
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_food_truck_profit()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")