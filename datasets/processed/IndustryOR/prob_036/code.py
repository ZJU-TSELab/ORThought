def optimize_microcomputers():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Microcomputers_Production")

    # Decision variables
    x_A = m.addVar(name="x_A", lb=10, ub=150, vtype=GRB.INTEGER)  # at least 10, at most 150
    x_B = m.addVar(name="x_B", lb=15, ub=70, vtype=GRB.INTEGER)  # at least 15, at most 70

    # Set the objective: maximize profit
    m.setObjective(300 * x_A + 450 * x_B, GRB.MAXIMIZE)

    # Add constraints
    # Process I: exactly 150 hours
    m.addConstr(4 * x_A + 6 * x_B == 150, name="Process_I")
    # Process II: exactly 70 hours
    m.addConstr(3 * x_A + 2 * x_B == 70, name="Process_II")
    # Profit constraint: at least $10,000
    m.addConstr(300 * x_A + 450 * x_B >= 10000, name="Profit_minimum")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
if __name__ == "__main__":
    result = optimize_microcomputers()
    if result is not None:
        print(f"Optimal total profit: {result}")
    else:
        print("No feasible solution found.")