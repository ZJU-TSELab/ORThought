def optimize_slime_production(
    flour_available=150,
    liquid_available=100,
    waste_limit=30
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("SlimeProduction")

    # Decision variables: number of times each beaker is used
    x1 = model.addVar(vtype=GRB.INTEGER, name="Beaker1")
    x2 = model.addVar(vtype=GRB.INTEGER, name="Beaker2")

    # Set objective: maximize total slime
    model.setObjective(5 * x1 + 3 * x2, GRB.MAXIMIZE)

    # Add resource constraints
    model.addConstr(4 * x1 + 6 * x2 <= flour_available, "FlourConstraint")
    model.addConstr(6 * x1 + 3 * x2 <= liquid_available, "LiquidConstraint")
    model.addConstr(4 * x1 + 2 * x2 <= waste_limit, "WasteConstraint")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
# Example usage 
if __name__ == "__main__":
    max_slime = optimize_slime_production()
    if max_slime is not None:
        print(f"Maximum Total Slime Produced: {max_slime}")
    else:
        print("No feasible solution found.")