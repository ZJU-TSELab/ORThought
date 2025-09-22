def optimize_milk_tea_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("MilkTeaOptimization")

    # Decision variables: number of bottles of black and matcha milk tea
    x = m.addVar(vtype=GRB.INTEGER, name="BlackMilkTea")
    y = m.addVar(vtype=GRB.INTEGER, name="MatchaMilkTea")

    # Set the objective: maximize profit
    m.setObjective(7.5 * x + 5 * y, GRB.MAXIMIZE)

    # Add constraints
    # Milk constraint
    m.addConstr(600 * x + 525 * y <= 30000, "MilkConstraint")
    # Honey constraint
    m.addConstr(10 * x + 5 * y <= 500, "HoneyConstraint")
    # Non-negativity is implicit in variable definition

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum profit
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_milk_tea_production()
    if max_profit is not None:
        print(f"Maximum Profit: ${max_profit}")
    else:
        print("No feasible solution found.")