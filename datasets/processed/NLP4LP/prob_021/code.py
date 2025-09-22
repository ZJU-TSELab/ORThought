def optimize_car_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Car_Production_Maximize_Profit")

    # Decision variables: number of regular and premium cars
    # Assuming production quantities are continuous; set vtype=GRB.CONTINUOUS
    x1 = m.addVar(name="Regular", vtype=GRB.CONTINUOUS, lb=0)
    x2 = m.addVar(name="Premium", vtype=GRB.CONTINUOUS, lb=0)

    # Set the objective: maximize profit
    profit_regular = 5000
    profit_premium = 8500
    m.setObjective(profit_regular * x1 + profit_premium * x2, GRB.MAXIMIZE)

    # Add demand constraints
    m.addConstr(x1 <= 8, name="Demand_Regular")
    m.addConstr(x2 <= 6, name="Demand_Premium")

    # Add production capacity constraint
    m.addConstr(x1 + x2 <= 12, name="Total_Capacity")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum profit value
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_car_production()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")