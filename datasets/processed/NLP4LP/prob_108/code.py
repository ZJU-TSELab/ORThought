def maximize_patients(time_available=15000, min_regular=50):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Maximize_Patients")

    # Decision variables: number of patients checked with each thermometer
    x = model.addVar(vtype=GRB.INTEGER, name="electronic")
    y = model.addVar(vtype=GRB.INTEGER, name="regular")

    # Set the objective: maximize total patients
    model.setObjective(x + y, GRB.MAXIMIZE)

    # Add constraints
    # Time constraint
    model.addConstr(3 * x + 2 * y <= time_available, "TimeLimit")
    # Accuracy constraint
    model.addConstr(x >= 2 * y, "Accuracy")
    # Minimum regular thermometer patients
    model.addConstr(y >= min_regular, "MinRegular")
    # Non-negativity is implicit in variable definition

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum number of patients served
        return int(model.objVal)
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