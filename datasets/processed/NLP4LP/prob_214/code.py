def optimize_pipes():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("WaterPipeOptimization")

    # Decision variables
    W = m.addVar(name="WidePipes", vtype=GRB.INTEGER, lb=5)
    N = m.addVar(name="NarrowPipes", vtype=GRB.INTEGER, lb=0)

    # Set objective: minimize total number of pipes
    m.setObjective(W + N, GRB.MINIMIZE)

    # Add constraints
    # Water capacity constraint
    m.addConstr(25 * W + 15 * N >= 900, name="WaterCapacity")
    # Ratio constraint: W <= N/3
    m.addConstr(3 * W <= N, name="PipeRatio")

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
        print(f"Minimum Total Pipes (Wide + Narrow): {min_pipes}")
    else:
        print("No feasible solution found.")