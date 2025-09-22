def optimize_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("fabric_plastic_production")

    # Decision variables: hours for Method A and Method B
    x = m.addVar(name="MethodA_hours", lb=0)
    y = m.addVar(name="MethodB_hours", lb=0)

    # Set the objective: minimize total hours
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add constraints
    # Fabric constraint
    m.addConstr(25 * x + 45 * y >= 1400, name="Fabric")
    # Plastic constraint
    m.addConstr(14 * x + 25 * y >= 1000, name="Plastic")
    # Special element constraint
    m.addConstr(60 * x + 65 * y <= 3500, name="SpecialElement")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total time
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_time = optimize_production()
    if min_time is not None:
        print(f"Minimum Total Production Time: {min_time}")
    else:
        print("No feasible solution found.")