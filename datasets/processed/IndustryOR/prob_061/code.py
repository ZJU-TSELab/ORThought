def optimize_restaurant_investment(revenue_A=15000,
                                   revenue_B=40000,
                                   revenue_C=30000,
                                   revenue_D=50000,
                                   cost_A=1.6,
                                   cost_B=2.5,
                                   cost_C=1.8,
                                   cost_D=3.0,
                                   budget=6):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Restaurant Investment Optimization")

    # Decision variables: binary for each restaurant
    y_A = model.addVar(vtype=GRB.BINARY, name="y_A")
    y_B = model.addVar(vtype=GRB.BINARY, name="y_B")
    y_C = model.addVar(vtype=GRB.BINARY, name="y_C")
    y_D = model.addVar(vtype=GRB.BINARY, name="y_D")

    # Set objective: maximize total revenue
    model.setObjective(
        revenue_A * y_A + revenue_B * y_B + revenue_C * y_C + revenue_D * y_D,
        GRB.MAXIMIZE)

    # Add budget constraint
    model.addConstr(cost_A * y_A + cost_B * y_B + cost_C * y_C + cost_D * y_D
                    <= budget,
                    name="BudgetConstraint")

    # Add mutual exclusivity constraint
    model.addConstr(y_A + y_D <= 1, name="MutualExclusion")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
if __name__ == "__main__":
    result = optimize_restaurant_investment()
    if result is not None:
        print(f"Optimal total revenue: {result}")
    else:
        print("No feasible solution found.")