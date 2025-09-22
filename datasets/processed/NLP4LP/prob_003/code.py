def optimize_cable_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("CableProduction")

    # Decision variables
    # Number of long cables
    L = m.addVar(name="LongCables", vtype=GRB.INTEGER, lb=10)
    # Number of short cables
    S = m.addVar(name="ShortCables", vtype=GRB.INTEGER, lb=0)

    # Set objective: maximize profit
    profit = 12 * L + 5 * S
    m.setObjective(profit, GRB.MAXIMIZE)

    # Add constraints
    # Gold constraint
    m.addConstr(10 * L + 7 * S <= 1000, name="GoldLimit")
    # Ratio constraint
    m.addConstr(S >= 5 * L, name="RatioConstraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum profit
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage 
if __name__ == "__main__":
    max_profit = optimize_cable_production()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")