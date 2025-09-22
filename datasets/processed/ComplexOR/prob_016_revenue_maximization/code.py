def optimize_package_sales(
    available_seats={
        'value': [50, 60, 70],
        'description': 'List of integers, available seats for each flight leg'
    },
    demand={
        'value': [30, 40],
        'description': 'List of integers, estimated demand for each package'
    },
    revenue={
        'value': [100, 150],
        'description':
        'List of integers, revenue gained for selling a unit of each package'
    },
    delta={
        'value': [[1, 1, 0], [0, 1, 1]],
        'description':
        '2D list of integers, 1 if package uses a specific flight leg, otherwise 0'
    }):
    from gurobipy import Model, GRB

    # Extract data
    seats = available_seats['value']
    demand_estimate = demand['value']
    revenues = revenue['value']
    delta_matrix = delta['value']

    num_packages = len(revenues)
    num_legs = len(seats)

    # Create model
    m = Model("PackageSales")
    m.setParam('OutputFlag', 0)  # Suppress output

    # Decision variables: number of units to sell for each package
    x = m.addVars(num_packages, vtype=GRB.INTEGER, lb=0, name="x")

    # Objective: maximize total revenue
    m.setObjective(sum(revenues[i] * x[i] for i in range(num_packages)),
                   GRB.MAXIMIZE)

    # Constraints: seat capacity for each flight leg
    for j in range(num_legs):
        m.addConstr(sum(delta_matrix[i][j] * x[i] for i in range(num_packages))
                    <= seats[j],
                    name=f"SeatLimit_leg{j}")

    # Demand constraints: do not sell more than estimated demand
    for i in range(num_packages):
        m.addConstr(x[i] <= demand_estimate[i], name=f"DemandLimit_package{i}")

    # Optimize
    m.optimize()

    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
if __name__ == "__main__":
    result = optimize_package_sales()
    print(f"Optimal Revenue: {result}")