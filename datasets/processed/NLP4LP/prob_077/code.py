def optimize_bottle_production(
    water_available=250000,
    min_glass_bottles=20,
    glass_bottle_volume=500,
    plastic_bottle_volume=750,
    plastic_ratio=3
):
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("WaterBottleOptimization")
    m.setParam('OutputFlag', 0)  # Suppress Gurobi output

    # Decision variables
    x = m.addVar(name="glass_bottles", vtype=GRB.INTEGER, lb=min_glass_bottles)
    y = m.addVar(name="plastic_bottles", vtype=GRB.INTEGER, lb=plastic_ratio * min_glass_bottles)

    # Set objective: maximize total bottles
    m.setObjective(x + y, GRB.MAXIMIZE)

    # Add water constraint
    m.addConstr(glass_bottle_volume * x + plastic_bottle_volume * y <= water_available, "WaterLimit")

    # Add ratio constraint: y >= 3x
    m.addConstr(y >= plastic_ratio * x, "PlasticRatio")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        total_bottles = m.objVal
        return total_bottles
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_bottles = optimize_bottle_production()
    if max_bottles is not None:
        print(f"Maximum Total Number of Bottles: {max_bottles}")
    else:
        print("No feasible solution found.")