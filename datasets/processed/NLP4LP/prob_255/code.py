def optimize_smoothies(
    acai_berries=3500,
    banana_chocolate=3200,
    water_limit=None  # Not explicitly given, so we omit this constraint
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Smoothie_Production_MinWater")

    # Decision variables
    x = model.addVar(name="acai_smoothies", vtype=GRB.INTEGER, lb=0)
    y = model.addVar(name="banana_smoothies", vtype=GRB.INTEGER, lb=0)

    # Set the objective: minimize total water used
    model.setObjective(3 * x + 4 * y, GRB.MINIMIZE)

    # Add resource constraints
    model.addConstr(7 * x <= acai_berries, name="Acai_Berries_Limit")
    model.addConstr(6 * y <= banana_chocolate, name="Banana_Choco_Limit")

    # Add popularity constraint: y > x
    # Since Gurobi does not handle strict inequalities directly,
    # we can approximate y >= x + epsilon, with epsilon > 0
    epsilon = 1e-5
    model.addConstr(y >= x + epsilon, name="Popularity_Constraint")

    # Add loyalty constraint: (13/7) * x >= y
    model.addConstr((13/7) * x >= y, name="Loyalty_Constraint")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        total_water = model.objVal
        return total_water
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_water = optimize_smoothies()
    if min_water is not None:
        print(f"Minimum Total Water Used: {min_water}")
    else:
        print("No feasible solution found.")