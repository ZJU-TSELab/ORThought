def production_optimization(products=['P1', 'P2'],
                            stages=['S1', 'S2'],
                            rate=[[2, 3], [3, 2]],
                            profit=[10, 20],
                            commit=[1, 2],
                            market=[5, 4],
                            avail=[10, 8]):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Production_Optimization")

    # Number of products and stages
    num_products = len(products)
    num_stages = len(stages)

    # Decision variables: production quantities for each product
    x = model.addVars(products, lb=0, vtype=GRB.CONTINUOUS, name="x")
    for i, p in enumerate(products):
        x[p].lb = commit[i]
        x[p].ub = market[i]

    # Set the objective: maximize total profit
    profit_expr = gp.quicksum(profit[i] * x[products[i]] for i in range(num_products))
    model.setObjective(profit_expr, GRB.MAXIMIZE)

    # Add stage hours constraints
    for s_idx, s in enumerate(stages):
        hours_expr = gp.quicksum(rate[p_idx][s_idx] * x[products[p_idx]] for p_idx in range(num_products))
        model.addConstr(hours_expr <= avail[s_idx], name=f"Stage_{s}_hours")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        total_profit = model.objVal
        return total_profit
    else:
        return None
if __name__ == "__main__":
    result = production_optimization()
    print(f"Optimal total profit: {result}")