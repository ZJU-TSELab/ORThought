def optimize_machines():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("IceCreamMachineOptimization")

    # Decision variables: number of each machine type
    x = m.addVar(vtype=GRB.INTEGER, name="Countertop", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="Fridge", lb=0)

    # Set the objective: minimize total number of machines
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add production constraint
    m.addConstr(80 * x + 150 * y >= 1000, name="ProductionRequirement")

    # Add heat constraint
    m.addConstr(50 * x + 70 * y <= 500, name="HeatLimit")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total number of machines
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_machines = optimize_machines()
    if min_machines is not None:
        print(f"Minimum Total Number of Machines: {min_machines}")
    else:
        print("No feasible solution found.")