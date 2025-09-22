def optimize_green_gas(
    red_liquid=80,
    blue_liquid=70,
    max_smelly_gas=10
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("GreenGasOptimization")

    # Decision variables: number of experiments (integer, >=0)
    x1 = model.addVar(vtype=GRB.INTEGER, name="Experiment1")
    x2 = model.addVar(vtype=GRB.INTEGER, name="Experiment2")

    # Set objective: maximize total green gas
    model.setObjective(5 * x1 + 6 * x2, GRB.MAXIMIZE)

    # Add resource constraints
    model.addConstr(3 * x1 + 5 * x2 <= red_liquid, "RedLiquid")
    model.addConstr(4 * x1 + 3 * x2 <= blue_liquid, "BlueLiquid")
    # Add smelly gas constraint
    model.addConstr(x1 + 2 * x2 <= max_smelly_gas, "SmellyGas")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_green_gas = optimize_green_gas()
    if max_green_gas is not None:
        print(f"Maximum Total Green Gas: {max_green_gas}")
    else:
        print("No feasible solution found.")