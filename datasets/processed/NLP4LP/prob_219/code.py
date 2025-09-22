def optimize_pills():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("PillOptimization")

    # Decision variables: number of calcium and vitamin D pills
    C = m.addVar(name="CalciumPills", vtype=GRB.INTEGER, lb=0)
    D = m.addVar(name="VitaminDPills", vtype=GRB.INTEGER, lb=0)

    # Set the objective: minimize total effective time
    m.setObjective(5 * C + 6 * D, GRB.MINIMIZE)

    # Add constraints
    m.addConstr(C + D >= 130, name="TotalPills")
    m.addConstr(D >= 40, name="MinVitaminD")
    m.addConstr(C >= D + 1, name="CalciumMoreThanVitaminD")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total time
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_time = optimize_pills()
    if min_time is not None:
        print(f"Minimum Total Effective Time: {min_time}")
    else:
        print("No feasible solution found.")