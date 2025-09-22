def optimize_worker_schedule():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("WorkerScheduling")

    # Decision variables: number of full-time and part-time workers
    F = m.addVar(vtype=GRB.INTEGER, name="FullTime")
    P = m.addVar(vtype=GRB.INTEGER, name="PartTime")

    # Set the objective: minimize total number of workers
    m.setObjective(F + P, GRB.MINIMIZE)

    # Add labor hours constraint
    m.addConstr(8 * F + 4 * P >= 500, name="LaborHours")

    # Add budget constraint
    m.addConstr(300 * F + 100 * P <= 15000, name="Budget")

    # Set non-negativity constraints (implicitly handled by variable types)
    # Solve the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total number of workers
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_workers = optimize_worker_schedule()
    if min_workers is not None:
        print(f"Minimum Total Number of Workers: {min_workers}")
    else:
        print("No feasible solution found.")