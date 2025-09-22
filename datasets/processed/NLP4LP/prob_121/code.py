def optimize_slime_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("SlimeProduction")

    # Decision variables: number of tables at each station
    x = m.addVar(name="Table1", lb=0)
    y = m.addVar(name="Table2", lb=0)

    # Set the objective: maximize total slime
    m.setObjective(4 * x + 5 * y, GRB.MAXIMIZE)

    # Add resource constraints
    m.addConstr(3 * x + 8 * y <= 100, name="Powder")
    m.addConstr(5 * x + 6 * y <= 90, name="Glue")
    m.addConstr(2 * x + 4 * y <= 30, name="Mess")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_slime = optimize_slime_production()
    if max_slime is not None:
        print(f"Maximum Slime Production: {max_slime}")
    else:
        print("No feasible solution found.")