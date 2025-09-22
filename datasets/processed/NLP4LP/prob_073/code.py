def optimize_experiments(metal_available=800, acid_available=750):
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Electricity_Production")

    # Decision variables: number of experiments for alpha and beta
    x = m.addVar(name="alpha_experiments", lb=0)
    y = m.addVar(name="beta_experiments", lb=0)

    # Set the objective: maximize total electricity
    m.setObjective(8 * x + 10 * y, GRB.MAXIMIZE)

    # Add constraints
    m.addConstr(3 * x + 5 * y <= metal_available, name="metal_constraint")
    m.addConstr(5 * x + 4 * y <= acid_available, name="acid_constraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum total electricity produced
        return m.objVal
    else:
        # No feasible solution found
        return None

# Example usage
if __name__ == "__main__":
    max_electricity = optimize_experiments()
    if max_electricity is not None:
        print(f"Maximum Total Electricity Produced: {max_electricity}")
    else:
        print("No feasible solution found.")