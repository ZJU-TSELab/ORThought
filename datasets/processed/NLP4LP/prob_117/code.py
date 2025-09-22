def optimize_hand_sanitizer_production(
    water_available=2000,
    alcohol_available=2100,
    max_liquid=30
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("SanitizerProduction")

    # Decision variables: number of liquid and foam sanitizers
    L = model.addVar(vtype=GRB.INTEGER, name="Liquid")
    F = model.addVar(vtype=GRB.INTEGER, name="Foam")

    # Set objective: maximize total cleaned hands
    model.setObjective(30 * L + 20 * F, GRB.MAXIMIZE)

    # Add resource constraints
    model.addConstr(40 * L + 60 * F <= water_available, "WaterLimit")
    model.addConstr(50 * L + 40 * F <= alcohol_available, "AlcoholLimit")

    # Add production constraints
    model.addConstr(F >= L + 1, "FoamExceedsLiquid")
    model.addConstr(L <= max_liquid, "LiquidMax")
    model.addConstr(L >= 0, "LiquidNonNeg")
    model.addConstr(F >= 0, "FoamNonNeg")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum number of hands cleaned
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_hands_cleaned = optimize_hand_sanitizer_production()
    if max_hands_cleaned is not None:
        print(f"Maximum Number of Hands Cleaned: {max_hands_cleaned}")
    else:
        print("No feasible solution found.")