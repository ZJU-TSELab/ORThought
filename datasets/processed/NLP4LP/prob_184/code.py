def optimize_bird_usage(
    min_pigeons=20,
    max_treats=1000,
    max_owl_ratio=0.4
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create model
    model = gp.Model("BirdLettersMaximization")
    model.setParam('OutputFlag', 0)  # Silence Gurobi output

    # Decision variables
    x = model.addVar(vtype=GRB.INTEGER, lb=min_pigeons, name="pigeons")
    y = model.addVar(vtype=GRB.INTEGER, lb=0, name="owls")

    # Objective: Maximize total letters sent
    model.setObjective(2 * x + 5 * y, GRB.MAXIMIZE)

    # Constraints
    # Treats constraint
    model.addConstr(3 * x + 5 * y <= max_treats, "TreatsLimit")
    # Owl ratio constraint: y <= (2/3) * x
    model.addConstr(y <= (2/3) * x, "OwlRatio")
    # Pigeons at least 20
    model.addConstr(x >= min_pigeons, "MinPigeons")

    # Optimize
    model.optimize()

    # Check feasibility and return result
    if model.status == GRB.OPTIMAL:
        total_letters = model.objVal
        return total_letters
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_letters = optimize_bird_usage()
    if max_letters is not None:
        print(f"Maximum Letters Sent: {max_letters}")
    else:
        print("No feasible solution found.")