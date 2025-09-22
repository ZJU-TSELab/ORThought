def optimize_pipes():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("PipeOptimization")

    # Decision variables: number of high-volume and low-volume pipes
    x = m.addVar(vtype=GRB.INTEGER, name="HighVolumePipes")
    y = m.addVar(vtype=GRB.INTEGER, name="LowVolumePipes")

    # Set the objective: minimize total number of pipes
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add demand constraint
    m.addConstr(10000 * x + 5000 * y >= 150000, name="DemandConstraint")

    # Add staffing constraint
    m.addConstr(12 * x + 5 * y <= 160, name="StaffingConstraint")

    # Add high-volume pipe proportion constraint: y ≥ (13/7) * x
    m.addConstr(y >= (13/7) * x, name="HighVolumeProportion")

    # Add minimum low-volume pipes constraint
    m.addConstr(y >= 8, name="MinLowVolumePipes")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total number of pipes
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_pipes = optimize_pipes()
    if min_pipes is not None:
        print(f"Minimum Total Pipes: {min_pipes}")
    else:
        print("No feasible solution found.")