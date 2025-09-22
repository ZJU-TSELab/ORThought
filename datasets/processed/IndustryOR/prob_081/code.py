def optimize_mall_leasing():
    from gurobipy import Model, GRB

    # Data
    area_per_store = [250, 350, 800, 400, 500]
    min_stores = [1, 1, 1, 0, 1]
    max_stores = [3, 2, 3, 2, 3]
    # Profit levels for each store type at 1, 2, 3 stores
    profit_levels = [
        [9, 8, 7],  # Jewelry
        [10, 9, None],  # Shoes & Hats (only up to 2 stores)
        [27, 21, 20],  # General Merchandise
        [16, 10, None],  # Bookstore
        [17, 15, 12]  # Catering
    ]

    # Initialize model
    model = Model("Mall Leasing Optimization")

    # Decision variables: number of stores for each type
    x = []
    for i in range(5):
        lb = min_stores[i]
        ub = max_stores[i]
        var = model.addVar(vtype=GRB.INTEGER, name=f"x_{i+1}", lb=lb, ub=ub)
        x.append(var)

    model.update()

    # Area constraint
    model.addConstr(sum(area_per_store[i] * x[i] for i in range(5)) <= 5000,
                    name="area_constraint")

    # For each store type, define profit per store based on x_i
    profit_per_store = []

    for i in range(5):
        # For store types with min=0 (store type 4), handle separately
        if min_stores[i] == 0:
            # For store type 4 (Bookstore), max=2
            # Create binary indicators for 1 and 2 stores
            b_1 = model.addVar(vtype=GRB.BINARY, name=f"b_{i+1}_1")
            b_2 = model.addVar(vtype=GRB.BINARY, name=f"b_{i+1}_2")
            model.update()

            # Link x_i to indicators
            # x_i = 1*b_1 + 2*b_2
            model.addConstr(x[i] == b_1 + 2 * b_2, name=f"link_x_b_{i+1}")

            # Exactly one indicator active if x_i > 0
            model.addConstr(b_1 + b_2 <= 1, name=f"one_indicator_{i+1}")

            # For x_i=0, both indicators are zero (no store)
            # For x_i=1 or 2, one indicator is 1
            # No need for additional constraints as above suffice

            # Define profit per store based on indicators
            profit_expr = 0
            if profit_levels[i][0] is not None:
                profit_expr += profit_levels[i][0] * b_1
            if profit_levels[i][1] is not None:
                profit_expr += profit_levels[i][1] * b_2
            # For 0 stores, profit per store is 0
            profit_per_store.append(profit_expr)

        else:
            # For store types with min >=1
            # Create binary indicators for counts 1, 2, 3
            indicators = []
            for count in range(1, 4):
                if count <= max_stores[i]:
                    b = model.addVar(vtype=GRB.BINARY, name=f"b_{i+1}_{count}")
                    indicators.append((count, b))
            model.update()

            # Link x_i to indicators
            model.addConstr(x[i] == sum(count * b for count, b in indicators),
                            name=f"link_x_b_{i+1}")

            # Exactly one indicator active
            model.addConstr(sum(b for _, b in indicators) == 1,
                            name=f"one_indicator_{i+1}")

            # Define profit per store based on indicator variables
            profit_expr = 0
            for count, b in indicators:
                profit_value = profit_levels[i][count - 1]
                profit_expr += profit_value * b
            profit_per_store.append(profit_expr)

    # Objective: maximize total rent income
    total_income = 0
    for i in range(5):
        total_income += 0.2 * profit_per_store[i] * x[i]

    model.setObjective(total_income, GRB.MAXIMIZE)

    # Optimize
    model.optimize()

    # Check solution status
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None

print(optimize_mall_leasing())