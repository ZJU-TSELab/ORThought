def optimize_amusement_park_machines():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("AmusementParkMachines")

    # Decision variables: number of each machine type
    x = m.addVar(vtype=GRB.INTEGER, name="cash_machines", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="card_machines", lb=0)

    # Set the objective: minimize total number of machines
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add constraints
    # Processing capacity constraint
    m.addConstr(20 * x + 30 * y >= 500, name="capacity")
    # Paper roll usage constraint
    m.addConstr(4 * x + 5 * y <= 90, name="paper")
    # Preference constraint
    m.addConstr(y <= x, name="preference")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimal total number of machines
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_machines = optimize_amusement_park_machines()
    if min_machines is not None:
        print(f"Minimum Total Number of Machines: {min_machines}")
    else:
        print("No feasible solution found.")