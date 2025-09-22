def optimize_foam(max_metal=200, max_acid=300, max_heat=50):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("FoamProduction")

    # Decision variables: number of cheap and expensive boxes
    x = model.addVar(vtype=GRB.INTEGER, name="CheapBoxes", lb=0)
    y = model.addVar(vtype=GRB.INTEGER, name="ExpensiveBoxes", lb=0)

    # Set the objective: maximize foam
    model.setObjective(8 * x + 10 * y, GRB.MAXIMIZE)

    # Add resource constraints
    model.addConstr(3 * x + 5 * y <= max_metal, "MetalConstraint")
    model.addConstr(5 * x + 8 * y <= max_acid, "AcidConstraint")
    model.addConstr(2 * x + 3 * y <= max_heat, "HeatConstraint")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_foam = optimize_foam()
    if max_foam is not None:
        print(f"Maximum Foam Produced: {max_foam}")
    else:
        print("No feasible solution found.")