def optimize_bridges():
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("BridgeBuildingOptimization")

    # Decision variables
    # x_b: number of beam bridges
    # x_t: number of truss bridges
    x_b = model.addVar(vtype=GRB.INTEGER, name="beam_bridges", lb=0)
    x_t = model.addVar(vtype=GRB.INTEGER, name="truss_bridges", lb=0)

    # Set objective: maximize total supported mass
    model.setObjective(40 * x_b + 60 * x_t, GRB.MAXIMIZE)

    # Add constraints
    # Material constraints
    model.addConstr(30 * x_b + 50 * x_t <= 600, "sticks_constraint")
    model.addConstr(5 * x_b + 8 * x_t <= 100, "glue_constraint")
    # Truss bridge limit
    model.addConstr(x_t <= 5, "max_truss")
    # Beam > Truss
    model.addConstr(x_b >= x_t + 1, "beam_greater_than_truss")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum total supported mass
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_mass = optimize_bridges()
    if max_mass is not None:
        print(f"Maximum Supported Mass: {max_mass}")
    else:
        print("No feasible solution found.")