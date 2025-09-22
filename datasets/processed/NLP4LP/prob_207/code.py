def optimize_taco_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Taco_Stand_Profit_Maximization")

    # Decision variables
    x1 = m.addVar(name="Regular_Tacos", lb=0)
    x2 = m.addVar(name="Deluxe_Tacos", lb=0)

    # Set objective: maximize profit
    profit = 2.50 * x1 + 3.55 * x2
    m.setObjective(profit, GRB.MAXIMIZE)

    # Add constraints
    m.addConstr(x1 <= 50, name="Demand_Regular")
    m.addConstr(x2 <= 40, name="Demand_Deluxe")
    m.addConstr(x1 + x2 <= 70, name="Total_Tacos")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_taco_production()
    if max_profit is not None:
        print(f"Maximum Profit: ${max_profit:.2f}")
    else:
        print("No feasible solution found.")