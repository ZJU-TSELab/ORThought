def optimize_factory_production():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("FactoryProductionMaxProfit")

    # Decision variables: production quantities of products I, II, III
    x_I = m.addVar(name="x_I", lb=0)
    x_II = m.addVar(name="x_II", lb=0)
    x_III = m.addVar(name="x_III", lb=0)

    # Set the objective: maximize total profit
    profit = 3 * x_I + 2 * x_II + 2.9 * x_III
    m.setObjective(profit, GRB.MAXIMIZE)

    # Add equipment capacity constraints
    m.addConstr(8 * x_I + 2 * x_II + 10 * x_III <= 300, name="A_capacity")
    m.addConstr(10 * x_I + 5 * x_II + 8 * x_III <= 400, name="B_capacity")
    m.addConstr(2 * x_I + 13 * x_II + 10 * x_III <= 420, name="C_capacity")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal profit value
        return m.objVal
    else:
        # No feasible solution found
        return None
if __name__ == "__main__":  
    result = optimize_factory_production()
    if result is not None:
        print(f"Optimal total profit: {result}")
    else:
        print("No feasible solution found.")