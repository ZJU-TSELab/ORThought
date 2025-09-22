def optimize_container_usage():
    from gurobipy import Model, GRB

    # Data
    demands = {'A': 120, 'B': 90, 'C': 300, 'D': 90, 'E': 120}
    weights = {'A': 0.5, 'B': 1.0, 'C': 0.4, 'D': 0.6, 'E': 0.65}
    max_containers = 20  # Sufficient upper bound

    M = 1e5  # Large number for big-M method

    # Initialize model
    model = Model("ContainerPacking")

    # Decision variables
    y = model.addVars(max_containers, vtype=GRB.BINARY,
                      name='y')  # Container usage
    z_A = model.addVars(max_containers, vtype=GRB.BINARY,
                        name='zA')  # Indicator for A loaded
    x = model.addVars(demands.keys(),
                      max_containers,
                      lb=0,
                      ub=GRB.INFINITY,
                      name='x')

    # Set objective: minimize number of containers used
    model.setObjective(y.sum(), GRB.MINIMIZE)

    # Demand constraints
    for i in demands:
        model.addConstr(sum(x[i, k] for k in range(max_containers))
                        >= demands[i],
                        name=f'demand_{i}')

    # Capacity and minimum load constraints
    for k in range(max_containers):
        # Capacity constraint
        model.addConstr(sum(weights[i] * x[i, k] for i in demands)
                        <= 60 * y[k],
                        name=f'capacity_{k}')
        # Minimum load constraint
        model.addConstr(sum(weights[i] * x[i, k] for i in demands)
                        >= 18 * y[k],
                        name=f'min_load_{k}')
        # D goods minimum per container
        model.addConstr(x['D', k] >= 12 * y[k], name=f'D_min_{k}')
        # A and C packaging constraints
        # If A is loaded, at least 1 unit of C
        model.addConstr(x['A', k] <= M * z_A[k], name=f'A_load_indicator_{k}')
        model.addConstr(x['C', k] >= z_A[k], name=f'C_condition_{k}')

    # Optional: limit goods to their total demand
    for i in demands:
        for k in range(max_containers):
            model.addConstr(x[i, k] <= demands[i], name=f'limit_{i}_{k}')

    # Optimize
    model.optimize()

    # Check feasibility and return the minimal number of containers
    if model.status == GRB.OPTIMAL:
        total_containers = sum(y[k].X for k in range(max_containers))
        return total_containers
    else:
        return None
if __name__ == "__main__":
    result = optimize_container_usage()
    if result is not None:
        print(f"Optimal number of containers used: {result}")
    else:
        print("No feasible solution found.")