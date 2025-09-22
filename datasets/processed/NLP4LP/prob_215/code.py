def optimize_transportation():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("TransportationOptimization")

    # Decision variables
    # x: number of carts
    # y: number of trolleys
    x = m.addVar(name="x", vtype=GRB.INTEGER, lb=0)
    y = m.addVar(name="y", vtype=GRB.INTEGER, lb=12)

    # Set objective: minimize total workers
    m.setObjective(2 * x + 4 * y, GRB.MINIMIZE)

    # Add constraints
    # Transportation capacity constraint
    m.addConstr(5 * x + 7 * y >= 100, name="capacity")
    # Proportion constraint: 2x >= 4.2 y
    m.addConstr(2 * x >= 4.2 * y, name="proportion")
    # y >= 12 is already enforced by lb=12

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total number of workers
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_workers = optimize_transportation()
    if min_workers is not None:
        print(f"Minimum Total Workers: {min_workers}")
    else:
        print("No feasible solution found.")