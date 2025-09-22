def optimize_furniture_factory():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Furniture_Production")

    # Decision variables
    T = m.addVar(vtype=GRB.INTEGER, name="Tables", lb=10)  # at least 10 tables
    C = m.addVar(vtype=GRB.INTEGER, name="Chairs", lb=0)
    B = m.addVar(vtype=GRB.INTEGER, name="Bookshelves",
                 lb=20)  # at least 20 bookshelves

    # Set the objective: maximize profit
    profit = 80 * T + 30 * C + 60 * B
    m.setObjective(profit, GRB.MAXIMIZE)

    # Add constraints
    # Warehouse space constraint
    m.addConstr(5 * T + 2 * C + 3 * B <= 500, "Space")
    # Total production limit
    m.addConstr(T + C + B <= 200, "TotalItems")
    # Demand constraints are already enforced via variable lower bounds

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
if __name__ == "__main__":
    result = optimize_furniture_factory()
    if result is not None:
        print(f"Optimal profit: {result}")
    else:
        print("No feasible solution found.")