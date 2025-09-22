def optimize_medication_time(
    min_total_units=100,
    min_anxiety_units=30,
    max_ratio=2
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Medication_Minimize_Time")

    # Decision variables: number of units of each medication
    x = model.addVar(name="x", lb=0, vtype=GRB.INTEGER)  # anxiety medication
    y = model.addVar(name="y", lb=0, vtype=GRB.INTEGER)  # anti-depressants

    # Set objective: minimize total time
    model.setObjective(3 * x + 5 * y, GRB.MINIMIZE)

    # Add constraints
    model.addConstr(x + y >= min_total_units, name="total_units")
    model.addConstr(x >= min_anxiety_units, name="min_anxiety")
    model.addConstr(x <= max_ratio * y, name="ratio_constraint")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the minimal total time
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_time = optimize_medication_time()
    if min_time is not None:
        print(f"Minimum Total Time: {min_time}")
    else:
        print("No feasible solution found.")