def maximize_patients(open_minutes=20000, time_auto=10, time_manual=15, min_auto=20):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("BloodPressureScheduling")

    # Decision variables
    x = model.addVar(name="automatic_patients", vtype=GRB.INTEGER, lb=0)
    y = model.addVar(name="manual_patients", vtype=GRB.INTEGER, lb=0)

    # Set objective: maximize total patients
    model.setObjective(x + y, GRB.MAXIMIZE)

    # Add constraints
    # Time constraint
    model.addConstr(time_auto * x + time_manual * y <= open_minutes, name="time_limit")
    # Manual patients at least twice automatic
    model.addConstr(y >= 2 * x, name="manual_at_least_twice_auto")
    # Minimum automatic patients
    model.addConstr(x >= min_auto, name="min_auto")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum number of patients served
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_patients = maximize_patients()
    if max_patients is not None:
        print(f"Maximum Number of Patients Served: {max_patients}")
    else:
        print("No feasible solution found.")