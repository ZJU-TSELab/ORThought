def optimize_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Production_Optimization")

    # Decision variables
    x_A = m.addVar(name="x_A", lb=0)  # Units of product A
    x_B = m.addVar(name="x_B", lb=0)  # Units of product B
    s_C = m.addVar(name="s_C", lb=0, ub=5)  # Units of by-product C sold
    d = m.addVar(name="d", lb=0)  # Units of C disposed

    # Set objective: maximize profit
    # profit = 4*x_A + 10*x_B + 3*s_C - 2*d
    m.setObjective(4 * x_A + 10 * x_B + 3 * s_C - 2 * d, GRB.MAXIMIZE)

    # Add constraints
    # Time constraints
    m.addConstr(2 * x_A + 3 * x_B <= 16, "Time_Process1")
    m.addConstr(3 * x_A + 4 * x_B <= 24, "Time_Process2")
    # By-product C sale limit
    m.addConstr(s_C <= 5, "Max_C_Sale")
    # C sold cannot exceed generated
    m.addConstr(s_C <= 2 * x_B, "C_Sale_Limit")
    # Disposal constraint
    m.addConstr(2 * x_B - s_C <= d, "Disposal_Constraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal profit value
        return m.objVal
    else:
        # No feasible solution
        return None
if __name__ == "__main__":
    result = optimize_production()
    if result is not None:
        print(f"Optimal profit: {result}")
    else:
        print("No feasible solution found.")