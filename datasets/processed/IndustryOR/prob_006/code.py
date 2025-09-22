def optimize_container_transportation():
    from gurobipy import Model, GRB

    # Data
    warehouses = ['Verona', 'Perugia', 'Rome', 'Pescara', 'Taranto', 'Lamezia']
    ports = ['Genoa', 'Venice', 'Ancona', 'Naples', 'Bari']

    supply = [10, 12, 20, 24, 18, 40]
    demand = [20, 15, 25, 33, 21]

    # Distances in km
    distances = [
        [290, 115, 355, 715, 810],  # Verona
        [380, 340, 165, 380, 610],  # Perugia
        [505, 530, 285, 220, 450],  # Rome
        [655, 450, 155, 240, 315],  # Pescara
        [1010, 840, 550, 305, 95],  # Taranto
        [1072, 1097, 747, 372, 333]  # Lamezia
    ]

    cost_per_km = 30

    # Initialize model
    m = Model("ContainerTransport")

    # Decision variables
    x = {}  # containers shipped from warehouse i to port j
    y = {}  # number of trucks on route i->j

    for i in range(len(warehouses)):
        for j in range(len(ports)):
            var_name_x = f"x_{i}_{j}"
            var_name_y = f"y_{i}_{j}"
            x[i, j] = m.addVar(vtype=GRB.INTEGER, lb=0, name=var_name_x)
            y[i, j] = m.addVar(vtype=GRB.INTEGER, lb=0, name=var_name_y)

    m.update()

    # Objective: minimize total transportation cost
    total_cost = 0
    for i in range(len(warehouses)):
        for j in range(len(ports)):
            c_ij = cost_per_km * distances[i][j]
            total_cost += c_ij * x[i, j]
    m.setObjective(total_cost, GRB.MINIMIZE)

    # Supply constraints
    for i in range(len(warehouses)):
        m.addConstr(sum(x[i, j] for j in range(len(ports))) <= supply[i],
                    name=f"Supply_{i}")

    # Demand constraints
    for j in range(len(ports)):
        m.addConstr(sum(x[i, j] for i in range(len(warehouses))) >= demand[j],
                    name=f"Demand_{j}")

    # Truck capacity constraints
    for i in range(len(warehouses)):
        for j in range(len(ports)):
            m.addConstr(x[i, j] <= 2 * y[i, j], name=f"TruckCap_{i}_{j}")

    # Optimize
    m.optimize()

    # Check feasibility and return result
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None

if __name__ == "__main__":
    result = optimize_container_transportation()
    if result is not None:
        print(f"Optimal transportation cost: {result}")
    else:
        print("No feasible solution found.")