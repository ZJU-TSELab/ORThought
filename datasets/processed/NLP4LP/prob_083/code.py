def optimize_chemical_reactions(
    inert_gas_available=1000,
    water_available=800
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Chemical_Reactions_Maximize_Compound")

    # Decision variables: number of reactions for A and B
    x = model.addVar(name="Reaction_A", lb=0)
    y = model.addVar(name="Reaction_B", lb=0)

    # Set the objective: maximize total rare compound produced
    model.setObjective(10 * x + 8 * y, GRB.MAXIMIZE)

    # Add resource constraints
    model.addConstr(5 * x + 7 * y <= inert_gas_available, name="InertGasConstraint")
    model.addConstr(6 * x + 3 * y <= water_available, name="WaterConstraint")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum amount of rare compound produced
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_compound = optimize_chemical_reactions()
    if max_compound is not None:
        print(f"Maximum Rare Compound Produced: {max_compound}")
    else:
        print("No feasible solution found.")