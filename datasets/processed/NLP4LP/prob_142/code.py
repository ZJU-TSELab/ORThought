def optimize_vans():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Vans Pollution Minimization")

    # Decision variables
    # x: number of old vans
    # y: number of new vans
    x = m.addVar(vtype=GRB.INTEGER, name="OldVans", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="NewVans", lb=0)

    # Set objective: minimize total pollution
    m.setObjective(50 * x + 30 * y, GRB.MINIMIZE)

    # Add constraints
    # Capacity constraint
    m.addConstr(100 * x + 80 * y >= 5000, "Capacity")
    # Max number of new vans
    m.addConstr(y <= 30, "MaxNewVans")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total pollution
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_pollution = optimize_vans()
    if min_pollution is not None:
        print(f"Minimum Total Pollution: {min_pollution}")
    else:
        print("No feasible solution found.")