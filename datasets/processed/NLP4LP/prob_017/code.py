def optimize_inventory(
    max_floor_space=400,
    profit_phone=120,
    profit_laptop=40,
    space_phone=1,
    space_laptop=4,
    max_budget=6000,
    cost_phone=400,
    cost_laptop=100,
    min_laptop_ratio=0.8
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("InventoryOptimization")

    # Decision variables: number of phones and laptops
    x = model.addVar(name="phones", vtype=GRB.INTEGER, lb=0)
    y = model.addVar(name="laptops", vtype=GRB.INTEGER, lb=0)

    # Set objective: maximize profit
    model.setObjective(profit_phone * x + profit_laptop * y, GRB.MAXIMIZE)

    # Add constraints
    # Floor space constraint
    model.addConstr(space_phone * x + space_laptop * y <= max_floor_space, "FloorSpace")
    # Stock composition constraint: y >= 4x (80% laptops)
    model.addConstr(y >= min_laptop_ratio * (x + y), "LaptopRatio")
    # Budget constraint
    model.addConstr(cost_phone * x + cost_laptop * y <= max_budget, "Budget")

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
    max_profit = optimize_inventory()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")