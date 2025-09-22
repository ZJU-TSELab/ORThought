def optimize_pills(pain_limit=6, anxiety_requirement=3):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Pill_Optimization")

    # Decision variables: number of pills of each type
    x1 = model.addVar(name="x1", lb=0, vtype=GRB.INTEGER)  # Type 1 pills
    x2 = model.addVar(name="x2", lb=0, vtype=GRB.INTEGER)  # Type 2 pills

    # Set the objective: minimize total discharge
    model.setObjective(0.3 * x1 + 0.1 * x2, GRB.MINIMIZE)

    # Add constraints
    # Pain medication constraint
    model.addConstr(0.2 * x1 + 0.6 * x2 <= pain_limit, name="PainLimit")
    # Anxiety medication constraint
    model.addConstr(0.3 * x1 + 0.2 * x2 >= anxiety_requirement, name="AnxietyReq")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal objective value (minimum discharge)
        return model.objVal
    else:
        # No feasible solution found
        return None

print(optimize_pills())