def optimize_alloy_blend(
    alloys_on_market={'value': [0, 1], 'description': 'list of alloy IDs'},
    required_elements={'value': ['A', 'B'], 'description': 'list of element IDs'},
    composition_data={'value': [[0.5, 0.5], [0.1, 0.9]], 'description': 'composition matrix'},
    desired_blend_percentage={'value': [0.5, 0.5], 'description': 'desired element percentages'},
    alloy_price={'value': [10.0, 20.0], 'description': 'alloy prices'}
):
    import gurobipy as gp
    from gurobipy import GRB

    # Extract data
    alloys = alloys_on_market['value']
    elements = required_elements['value']
    composition = composition_data['value']
    desired = desired_blend_percentage['value']
    prices = alloy_price['value']

    n_alloys = len(alloys)
    n_elements = len(elements)

    # Create model
    model = gp.Model("Alloy_Blend_Optimization")
    model.setParam('OutputFlag', 0)  # Silence output

    # Decision variables: amount of each alloy to purchase
    x = model.addVars(n_alloys, lb=0, name='x')

    # Objective: minimize total cost
    model.setObjective(
        gp.quicksum(prices[i] * x[i] for i in range(n_alloys)),
        GRB.MINIMIZE
    )

    # Constraint: total amount purchased equals 1
    model.addConstr(gp.quicksum(x[i] for i in range(n_alloys)) == 1, name='TotalAmount')

    # Constraints: blend percentage for each element
    for k in range(n_elements):
        # sum over alloys of composition * amount = desired percentage
        model.addConstr(
            gp.quicksum(composition[i][k] * x[i] for i in range(n_alloys)) == desired[k],
            name=f'Blend_{elements[k]}'
        )

    # Optimize
    model.optimize()

    # Check feasibility and return optimal value
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None

if __name__ == "__main__":
    result = optimize_alloy_blend()
    if result is not None:
        print(f"Minimum total cost: {result}")
    else:
        print("No feasible solution found.")