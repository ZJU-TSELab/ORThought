def optimize_sand_delivery():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("SandDelivery")

    # Decision variables
    # x_s: number of small containers
    # x_l: number of large containers
    x_s = m.addVar(vtype=GRB.INTEGER, name="x_s")
    x_l = m.addVar(vtype=GRB.INTEGER, name="x_l")

    # Set objective: maximize total sand
    m.setObjective(20 * x_s + 50 * x_l, GRB.MAXIMIZE)

    # Add constraints
    # Container ratio constraint
    m.addConstr(x_s == 3 * x_l, "ratio")
    # Minimum containers
    m.addConstr(x_s >= 5, "min_small")
    m.addConstr(x_l >= 3, "min_large")
    # Labor constraint
    m.addConstr(x_s + 3 * x_l <= 100, "labor")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum amount of sand delivered
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_sand = optimize_sand_delivery()
    if max_sand is not None:
        print(f"Maximum Amount of Sand Delivered: {max_sand}")
    else:
        print("No feasible solution found.")