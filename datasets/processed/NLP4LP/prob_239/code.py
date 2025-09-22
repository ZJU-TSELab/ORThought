def optimize_soda_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("SodaProduction")

    # Decision variables
    x = m.addVar(name="cans", vtype=GRB.INTEGER, lb=0)
    y = m.addVar(name="bottles", vtype=GRB.INTEGER, lb=0)

    # Set objective: maximize total units
    m.setObjective(x + y, GRB.MAXIMIZE)

    # Add constraints
    # Total volume constraint
    m.addConstr(250 * x + 1000 * y >= 1_000_000, name="volume_constraint")
    # Ratio constraint: cans >= 3 * bottles
    m.addConstr(x >= 3 * y, name="ratio_constraint")
    # Minimum bottles
    m.addConstr(y >= 100, name="min_bottles")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum total units produced
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_units = optimize_soda_production()
    if max_units is not None:
        print(f"Maximum Total Units Produced (Cans + Bottles): {max_units}")
    else:
        print("No feasible solution found.")