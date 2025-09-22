def optimize_jam_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("JamProduction")

    # Decision variables
    # x: number of small packet sets
    # y: number of jugs
    x = m.addVar(name="x", vtype=GRB.INTEGER, lb=35)  # at least 35 small packets
    y = m.addVar(name="y", vtype=GRB.INTEGER, lb=0)

    # Set objective: maximize total units
    m.setObjective(x + y, GRB.MAXIMIZE)

    # Constraints
    # Jam volume constraint
    m.addConstr(1000 * x + 1250 * y <= 65000, name="jam_volume")
    # Ratio constraint: at least 3 times as many jugs as small packets
    m.addConstr(y >= 3 * x, name="ratio_constraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum total units sold
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_units = optimize_jam_production()
    if max_units is not None:
        print(f"Maximum Total Units Sold (Small Packets + Jugs): {max_units}")
    else:
        print("No feasible solution found.")