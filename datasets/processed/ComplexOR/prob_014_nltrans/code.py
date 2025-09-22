def transportation_optimization(supply=None, demand=None, rate=None, limit=None):
    from gurobipy import Model, GRB, quicksum

    # Default data based on provided sample
    if supply is None:
        supply = {'value': [20, 30]}
    if demand is None:
        demand = {'value': [30, 20]}
    if rate is None:
        rate = {'value': [[8, 6], [5, 10]]}
    if limit is None:
        limit = {'value': [[15, 25], [25, 20]]}

    Supply = supply['value']
    Demand = demand['value']
    Rate = rate['value']
    Limit = limit['value']

    num_origins = len(Supply)
    num_destinations = len(Demand)

    # Create model
    m = Model("TransportationProblem")
    m.setParam('OutputFlag', 0)  # Suppress output

    # Decision variables: x[i,j]
    x = {}
    for i in range(num_origins):
        for j in range(num_destinations):
            var_name = f"x_{i}_{j}"
            x[i,j] = m.addVar(lb=0, ub=Limit[i][j], vtype=GRB.CONTINUOUS, name=var_name)

    m.update()

    # Objective: Minimize total cost
    m.setObjective(
        quicksum(Rate[i][j] * x[i,j] for i in range(num_origins) for j in range(num_destinations)),
        GRB.MINIMIZE
    )

    # Supply constraints
    for i in range(num_origins):
        m.addConstr(
            quicksum(x[i,j] for j in range(num_destinations)) <= Supply[i],
            name=f"Supply_{i}"
        )

    # Demand constraints
    for j in range(num_destinations):
        m.addConstr(
            quicksum(x[i,j] for i in range(num_origins)) >= Demand[j],
            name=f"Demand_{j}"
        )

    # Optimize the model
    m.optimize()

    # Check feasibility and return optimal value
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    result = transportation_optimization()
    print(f"Optimal cost: {result}")