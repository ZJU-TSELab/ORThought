def optimize_oil_production(
    total_land=300,
    max_drill_bits=2500,
    max_pollution=4500
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Oil_Well_Allocation")

    # Decision variables: acres for small and large wells
    x = model.addVar(name="small_wells_acres", lb=0)
    y = model.addVar(name="large_wells_acres", lb=0)

    # Set objective: maximize total oil production
    model.setObjective(2 * x + 5 * y, GRB.MAXIMIZE)

    # Add constraints
    # Land constraint
    model.addConstr(x + y <= total_land, name="land_constraint")
    # Drill bits constraint
    model.addConstr(5 * x + 10 * y <= max_drill_bits, name="drill_bits_constraint")
    # Pollution constraint
    model.addConstr(10 * x + 20 * y <= max_pollution, name="pollution_constraint")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal total oil production
        return model.objVal
    else:
        # No feasible solution found
        return None

# Example usage
if __name__ == "__main__":
    max_oil_production = optimize_oil_production()
    if max_oil_production is not None:
        print(f"Maximum Total Oil Production: {max_oil_production}")
    else:
        print("No feasible solution found.")