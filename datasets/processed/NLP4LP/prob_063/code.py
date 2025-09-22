def optimize_co2_production(
    wood_available=300,
    oxygen_available=300,
    co2_with_catalyst=15,
    co2_without_catalyst=18,
    wood_per_with=10,
    oxygen_per_with=20,
    wood_per_without=15,
    oxygen_per_without=12
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("CO2_Production_Maximization")

    # Decision variables: number of times to run each process
    x = model.addVar(name="with_catalyst")
    y = model.addVar(name="without_catalyst")

    # Set objective: maximize total CO2
    model.setObjective(
        co2_with_catalyst * x + co2_without_catalyst * y,
        GRB.MAXIMIZE
    )

    # Add resource constraints
    model.addConstr(wood_per_with * x + wood_per_without * y <= wood_available, "WoodConstraint")
    model.addConstr(oxygen_per_with * x + oxygen_per_without * y <= oxygen_available, "OxygenConstraint")

    # Set non-negativity constraints (implicit in variable definitions)
    model.addConstr(x >= 0, "X_nonneg")
    model.addConstr(y >= 0, "Y_nonneg")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum CO2 produced
        return model.objVal
    else:
        # No feasible solution
        return None

# Example usage
if __name__ == "__main__":
    max_co2 = optimize_co2_production()
    if max_co2 is not None:
        print(f"Maximum CO2 produced: {max_co2:.2f}")
    else:
        print("No feasible solution found.")