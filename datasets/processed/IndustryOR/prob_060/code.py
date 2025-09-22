def optimize_production():
    from gurobipy import Model, GRB

    # Data from the problem
    prep_costs = {'A': 1000, 'B': 920, 'C': 800, 'D': 700}
    unit_costs = {'A': 20, 'B': 24, 'C': 16, 'D': 28}
    capacities = {'A': 900, 'B': 1000, 'C': 1200, 'D': 1600}
    total_units = 2000

    # Initialize model
    m = Model("Production_Optimization")
    m.setParam('OutputFlag', 0)  # Suppress output

    # Decision variables
    y = m.addVars(prep_costs.keys(), vtype=GRB.BINARY, name='y')
    x = m.addVars(prep_costs.keys(), lb=0, vtype=GRB.INTEGER, name='x')

    # Objective function
    m.setObjective(
        sum(prep_costs[i] * y[i] + unit_costs[i] * x[i] for i in prep_costs),
        GRB.MINIMIZE)

    # Constraints
    # Demand satisfaction
    m.addConstr(sum(x[i] for i in prep_costs) == total_units, name='Demand')

    # Capacity constraints linked with activation
    for i in prep_costs:
        m.addConstr(x[i] <= capacities[i] * y[i], name=f'Cap_{i}')

    # Optimize
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        total_cost = m.objVal
        return total_cost
    else:
        return None
if __name__ == "__main__":
    result = optimize_production()
    if result is not None:
        print(f"Optimal total cost for production: {result}")
    else:
        print("No feasible solution found.")