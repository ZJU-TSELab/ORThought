def optimize_pills():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("pharmacy_pills")

    # Decision variables: number of pills
    x = m.addVar(name="painkiller", lb=50, vtype=GRB.INTEGER)
    y = m.addVar(name="sleeping", lb=0, vtype=GRB.INTEGER)

    # Set objective: minimize total digestive medicine
    m.setObjective(3 * x + 5 * y, GRB.MINIMIZE)

    # Add constraints
    # Morphine constraint
    m.addConstr(10 * x + 6 * y <= 3000, name="morphine_limit")
    # Sleeping pills ≥ 70% of total pills
    m.addConstr(y >= (7/3) * x, name="sleeping_ratio")
    # x ≥ 50 is already enforced by lb=50

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_digestive_medicine = optimize_pills()
    if min_digestive_medicine is not None:
        print(f"Minimum Total Digestive Medicine: {min_digestive_medicine}")
    else:
        print("No feasible solution found.")