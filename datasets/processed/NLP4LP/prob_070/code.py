def optimize_machines():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("HandSanitizerMachines")

    # Decision variables
    # x: number of motion-activated machines (minimum 3)
    x = m.addVar(vtype=GRB.INTEGER, name="x", lb=3)
    # y: number of manual machines (non-negative)
    y = m.addVar(vtype=GRB.INTEGER, name="y", lb=0)

    # Set objective: minimize total number of machines
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add constraints
    # Delivery constraint
    m.addConstr(50 * x + 75 * y >= 1000, name="delivery")
    # Power constraint
    m.addConstr(30 * x + 20 * y <= 500, name="power")
    # Manual proportion constraint
    m.addConstr(y <= (2.0/3.0) * x, name="manual_ratio")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        total_machines = m.objVal
        return total_machines
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_machines = optimize_machines()
    if min_machines is not None:
        print(f"Minimum Total Number of Machines: {min_machines}")
    else:
        print("No feasible solution found.")