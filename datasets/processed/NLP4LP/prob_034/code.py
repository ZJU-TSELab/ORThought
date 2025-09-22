def optimize_berry_farm(
    total_acres=300,
    budget=10000,
    labor_days=575,
    profit_blueberry=56,
    profit_raspberry=75,
    watering_cost_blueberry=22,
    watering_cost_raspberry=25,
    labor_blueberry=6,
    labor_raspberry=3
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("BerryFarmOptimization")

    # Decision variables: acres of blueberries and raspberries
    x = model.addVar(name="Blueberries", lb=0)
    y = model.addVar(name="Raspberries", lb=0)

    # Set the objective: maximize profit
    model.setObjective(profit_blueberry * x + profit_raspberry * y, GRB.MAXIMIZE)

    # Add constraints
    # Land constraint
    model.addConstr(x + y <= total_acres, name="Land")
    # Watering cost constraint
    model.addConstr(watering_cost_blueberry * x + watering_cost_raspberry * y <= budget, name="Watering")
    # Labor constraint
    model.addConstr(labor_blueberry * x + labor_raspberry * y <= labor_days, name="Labor")

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
    max_profit = optimize_berry_farm()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")