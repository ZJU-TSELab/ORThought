def optimize_machine_hours(
    production_eye_target=1300,
    production_foot_target=1500,
    water_available=1200
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Machine_Usage_Minimization")

    # Decision variables: hours of machine 1 and machine 2
    x1 = model.addVar(name="x1", lb=0)
    x2 = model.addVar(name="x2", lb=0)
    max_hour = model.addVar(name="max_hour", lb=0)

    # Set objective: minimize total hours
    model.setObjective(max_hour, GRB.MINIMIZE)

    # Add production constraints
    model.addConstr(30 * x1 + 45 * x2 >= production_eye_target, name="EyeCream")
    model.addConstr(60 * x1 + 30 * x2 >= production_foot_target, name="FootCream")

    # Add water constraint
    model.addConstr(20 * x1 + 15 * x2 <= water_available, name="WaterLimit")

    # Add maximum hour constraints
    model.addConstr(max_hour >= x1, name="MaxHour_x1")
    model.addConstr(max_hour >= x2, name="MaxHour_x2")
    
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
print(optimize_machine_hours())