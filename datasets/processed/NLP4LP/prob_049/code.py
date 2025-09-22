def optimize_snow_removers():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("SnowRemovers")

    # Decision variables: number of seasonal and permanent workers
    x = m.addVar(vtype=GRB.INTEGER, name="Seasonal")
    y = m.addVar(vtype=GRB.INTEGER, name="Permanent")

    # Set the objective: minimize total number of workers
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add constraints
    # Labor hours constraint
    m.addConstr(6 * x + 10 * y >= 300, name="LaborHours")
    # Budget constraint
    m.addConstr(120 * x + 250 * y <= 6500, name="Budget")
    # Non-negativity constraints are implicit for integer variables in Gurobi

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total number of workers
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_workers = optimize_snow_removers()
    if min_workers is not None:
        print(f"Minimum Total Number of Workers: {min_workers}")
    else:
        print("No feasible solution found.")