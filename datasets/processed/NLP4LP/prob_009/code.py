def optimize_package_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Grocery_Packages")

    # Decision variables: number of packages (integer, ≥ 0)
    x = m.addVar(vtype=GRB.INTEGER, name="banana_haters")
    y = m.addVar(vtype=GRB.INTEGER, name="combo")

    # Set objective: maximize total profit
    m.setObjective(6 * x + 7 * y, GRB.MAXIMIZE)

    # Add constraints
    # Apples constraint
    m.addConstr(6 * x + 5 * y <= 10, "apple_limit")
    # Grapes constraint
    m.addConstr(30 * x + 20 * y <= 80, "grape_limit")
    # Bananas constraint
    m.addConstr(6 * y <= 20, "banana_limit")
    # Non-negativity is implicit in variable definition

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None

# Example usage
if __name__ == "__main__":
    max_profit = optimize_package_production()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")