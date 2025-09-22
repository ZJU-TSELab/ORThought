def optimize_shampoo_ingredients():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("shampoo_optimization")

    # Decision variables: number of units of sulfate and ginger
    S = m.addVar(name="S", lb=0, vtype=GRB.INTEGER)
    G = m.addVar(name="G", lb=0, vtype=GRB.INTEGER)

    # Set the objective: minimize total effective time
    m.setObjective(0.5 * S + 0.75 * G, GRB.MINIMIZE)

    # Add constraints
    m.addConstr(S >= 100, name="min_sulfate")
    m.addConstr(S + G == 400, name="total_units")
    m.addConstr(S <= 2 * G, name="max_sulfate_ratio")

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
    min_time = optimize_shampoo_ingredients()
    if min_time is not None:
        print(f"Minimum Total Effective Time: {min_time}")
    else:
        print("No feasible solution found.")