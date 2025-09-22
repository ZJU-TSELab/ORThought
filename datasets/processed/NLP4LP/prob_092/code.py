def optimize_bone_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("BoneProduction")

    # Decision variables
    # x: number of small bones
    # y: number of large bones
    x = m.addVar(vtype=GRB.INTEGER, name="small_bones", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="large_bones", lb=30)

    # Set objective: minimize total meat
    m.setObjective(12 * x + 15 * y, GRB.MINIMIZE)

    # Add constraints
    # Tooth medication constraint
    m.addConstr(10 * x + 15 * y <= 2000, "tooth_limit")
    # Ratio constraint: at least 50% small bones
    m.addConstr(x >= y, "small_ratio")
    # Minimum large bones
    m.addConstr(y >= 30, "min_large_bones")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total meat used
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_meat = optimize_bone_production()
    if min_meat is not None:
        print(f"Minimum Total Meat Used: {min_meat}")
    else:
        print("No feasible solution found.")