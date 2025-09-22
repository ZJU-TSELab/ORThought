def optimize_media_selection(target_audiences=None,
                             advertising_media=None,
                             incidence_matrix=None,
                             media_costs=None):
    from gurobipy import Model, GRB, quicksum

    # Set default data if not provided
    if target_audiences is None:
        target_audiences = {'value': [0, 1, 2], 'description': 'List of target audiences'}
    if advertising_media is None:
        advertising_media = {'value': [0, 1, 2], 'description': 'List of advertising media'}
    if incidence_matrix is None:
        incidence_matrix = {'value': [[1, 0, 1], [1, 1, 0], [0, 1, 1]],
                            'description': 'Incidence matrix'}
    if media_costs is None:
        media_costs = {'value': [10, 15, 20], 'description': 'Media costs'}

    T = target_audiences['value']
    M = advertising_media['value']
    A = incidence_matrix['value']
    C = media_costs['value']

    # Initialize model
    model = Model("MediaSelection")
    model.setParam('OutputFlag', 0)  # Suppress output

    # Decision variables: y_m = 1 if media m is selected
    y_vars = {}
    for m_idx in M:
        y_vars[m_idx] = model.addVar(vtype=GRB.BINARY, name=f'y_{m_idx}')

    model.update()

    # Objective: Minimize total cost
    model.setObjective(
        quicksum(C[m_idx] * y_vars[m_idx] for m_idx in M),
        GRB.MINIMIZE
    )

    # Coverage constraints: each audience must be covered at least once
    for t_idx, t in enumerate(T):
        coverage_expr = quicksum(A[t_idx][m_idx] * y_vars[m_idx] for m_idx in M)
        model.addConstr(coverage_expr >= 1, name=f'cover_{t}')

    # Optimize
    model.optimize()

    # Check feasibility and return result
    if model.status == GRB.OPTIMAL:
        total_cost = model.objVal
        return total_cost
    else:
        return None
if __name__ == "__main__":
    result = optimize_media_selection()
    if result is not None:
        print(f"Minimum total cost: {result}")
    else:
        print("No feasible solution found.")