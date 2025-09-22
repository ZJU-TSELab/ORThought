def optimize_bakery_production(
    max_machine_hours=3000,
    profit_bread=5,
    profit_cookies=3,
    bread_mixer_time=1,
    cookies_mixer_time=0.5,
    bread_oven_time=3,
    cookies_oven_time=1
):
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("BakeryOptimization")

    # Decision variables: number of loaves of bread and batches of cookies
    x = m.addVar(name="Bread", lb=0)
    y = m.addVar(name="Cookies", lb=0)

    # Set the objective: maximize profit
    m.setObjective(profit_bread * x + profit_cookies * y, GRB.MAXIMIZE)

    # Add constraints
    # Stand-mixer constraint
    m.addConstr(bread_mixer_time * x + cookies_mixer_time * y <= max_machine_hours, "MixerTime")
    # Oven constraint
    m.addConstr(bread_oven_time * x + cookies_oven_time * y <= max_machine_hours, "OvenTime")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal profit
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_bakery_production()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")