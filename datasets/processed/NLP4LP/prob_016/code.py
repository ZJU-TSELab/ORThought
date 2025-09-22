def optimize_model_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Model_Production")

    # Decision variables: number of trains and planes (integer, >= 0)
    x = m.addVar(vtype=GRB.INTEGER, name="Trains")
    y = m.addVar(vtype=GRB.INTEGER, name="Planes")

    # Set the objective: maximize profit
    m.setObjective(8 * x + 10 * y, GRB.MAXIMIZE)

    # Add resource constraints
    m.addConstr(3 * x + 4 * y <= 120, name="Wood")
    m.addConstr(3 * x + 2 * y <= 90, name="Paint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_model_production()
    if max_profit is not None:
        print(f"Maximum Profit: {max_profit}")
    else:
        print("No feasible solution found.")