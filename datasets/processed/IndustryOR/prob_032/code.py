def minimize_inheritance_difference():
    from gurobipy import Model, GRB

    # Item values
    values = {
        'painting': 25000,
        'bust': 5000,
        'vase': 20000,
        'porsche': 40000,
        'diamond1': 12000,
        'diamond2': 12000,
        'diamond3': 12000,
        'sofa': 3000,
        'dog1': 3000,
        'dog2': 3000,
        'sculpture': 10000,
        'boat': 15000,
        'motorcycle': 10000,
        'cavour_furniture': 13000
    }

    # Initialize model
    m = Model("InheritancePartition")
    m.setParam('OutputFlag', 0)  # Silence output

    # Decision variables: y_i for each item
    y_vars = {}
    for item in values:
        y_vars[item] = m.addVar(vtype=GRB.BINARY, name=f'y_{item}')

    # Auxiliary variable for absolute difference
    d = m.addVar(vtype=GRB.CONTINUOUS, name='d')

    m.update()

    # Total value
    V_total = sum(values.values())

    # Objective: minimize d
    m.setObjective(d, GRB.MINIMIZE)

    # Constraints for absolute difference linearization
    sum_values_y = sum(values[item] * y_vars[item] for item in values)
    m.addConstr(2 * sum_values_y - V_total <= d, "abs_diff_upper")
    m.addConstr(-(2 * sum_values_y - V_total) <= d, "abs_diff_lower")

    # Constraint: dogs must stay together
    m.addConstr(y_vars['dog1'] == y_vars['dog2'], "dogs_together")

    # Optimize
    m.optimize()

    if m.status == GRB.OPTIMAL:
        # Return the minimal difference
        return m.objVal
    else:
        return None
if __name__ == "__main__":
    result = minimize_inheritance_difference()
    if result is not None:
        print(f"Minimal inheritance difference: {result}")
    else:
        print("No feasible solution found.")