def solve_multi_commodity_transport(
    supply_data={'value': [[20, 30], [40, 10]], 'description': 'supply per origin and product'},
    demand_data={'value': [[30, 30], [30, 10]], 'description': 'demand per destination and product'},
    limit_data={'value': [[35, 25], [20, 30]], 'description': 'shipment limits per origin-destination pair'},
    cost_data={'value': [[[2, 3], [4, 1]], [[3, 2], [2, 4]]], 'description': 'cost per unit for each origin-destination-product'}
):
    import gurobipy as gp
    from gurobipy import GRB

    # Extract data
    supply = supply_data['value']
    demand = demand_data['value']
    limit = limit_data['value']
    cost = cost_data['value']

    num_origins = len(supply)
    num_destinations = len(demand)
    num_products = len(supply[0])

    # Create model
    model = gp.Model("MultiCommodityTransportation")

    # Decision variables: x[i,j,p]
    x = model.addVars(
        range(num_origins),
        range(num_destinations),
        range(num_products),
        lb=0,
        name="x"
    )

    # Objective: minimize total shipping cost
    model.setObjective(
        gp.quicksum(
            cost[i][j][p] * x[i,j,p]
            for i in range(num_origins)
            for j in range(num_destinations)
            for p in range(num_products)
        ),
        GRB.MINIMIZE
    )

    # Supply constraints
    for i in range(num_origins):
        for p in range(num_products):
            model.addConstr(
                gp.quicksum(x[i,j,p] for j in range(num_destinations)) == supply[i][p],
                name=f"Supply_{i}_Product_{p}"
            )

    # Demand constraints
    for j in range(num_destinations):
        for p in range(num_products):
            model.addConstr(
                gp.quicksum(x[i,j,p] for i in range(num_origins)) == demand[j][p],
                name=f"Demand_{j}_Product_{p}"
            )

    # Limit constraints
    for i in range(num_origins):
        for j in range(num_destinations):
            model.addConstr(
                gp.quicksum(x[i,j,p] for p in range(num_products)) <= limit[i][j],
                name=f"Limit_{i}_{j}"
            )

    # Optimize the model
    model.optimize()

    # Return the optimal objective value if feasible
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
if __name__ == "__main__":
    result = solve_multi_commodity_transport()
    if result is not None:
        print(f"Optimal objective value: {result}")
    else:
        print("No feasible solution found.")