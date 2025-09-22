def minimize_radiation(prep_time_limit=400, exec_time_limit=500):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Minimize_Radiation")

    # Decision variables: number of experiments
    x = model.addVar(vtype=GRB.INTEGER, name="InVivo")
    y = model.addVar(vtype=GRB.INTEGER, name="ExVivo")

    # Set objective: minimize total radiation
    model.setObjective(2 * x + 3 * y, GRB.MINIMIZE)

    # Add preparation time constraint
    model.addConstr(30 * x + 45 * y <= prep_time_limit, "PrepTimeLimit")

    # Add execution time constraint
    model.addConstr(60 * x + 30 * y <= exec_time_limit, "ExecTimeLimit")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_radiation = minimize_radiation()
    if min_radiation is not None:
        print(f"Minimum Total Radiation: {min_radiation}")
    else:
        print("No feasible solution found.")