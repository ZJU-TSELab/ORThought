def optimize_mining_proportions():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("MiningOptimization")

    # Decision variables: proportions of land allocated to each technique
    x = m.addVar(name="heap_leaching", lb=0)
    y = m.addVar(name="vat_leaching", lb=0)

    # Set the objective: maximize total REO production
    m.setObjective(300 * x + 500 * y, GRB.MAXIMIZE)

    # Add constraints
    # Land constraint
    m.addConstr(x + y <= 1, name="land_constraint")
    # Machine constraint
    m.addConstr(1000 * x + 2000 * y <= 100, name="machine_constraint")
    # Wastewater constraint
    m.addConstr(800 * x + 1700 * y <= 90, name="wastewater_constraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum production value
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_production = optimize_mining_proportions()
    if max_production is not None:
        print(f"Maximum REO Production: {max_production}")
    else:
        print("No feasible solution found.")