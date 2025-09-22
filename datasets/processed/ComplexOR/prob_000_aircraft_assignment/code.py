def aircraft_assignment(
    availability=[2, 3, 1],
    demand=[100, 150],
    capabilities=[[50, 70], [60, 80], [70, 90]],
    costs=[[100, 200], [150, 250], [200, 300]]
):
    import gurobipy as gp
    from gurobipy import GRB

    num_aircraft = len(availability)
    num_routes = len(demand)

    # Create model
    model = gp.Model("AircraftAssignment")

    # Decision variables: x[i,j] - number of aircraft of type i assigned to route j
    x = model.addVars(
        range(num_aircraft),
        range(num_routes),
        vtype=GRB.INTEGER,
        lb=0,
        name="x"
    )

    # Objective: minimize total cost
    model.setObjective(
        gp.quicksum(costs[i][j] * x[i, j] for i in range(num_aircraft) for j in range(num_routes)),
        GRB.MINIMIZE
    )

    # Availability constraints
    for i in range(num_aircraft):
        model.addConstr(
            gp.quicksum(x[i, j] for j in range(num_routes)) <= availability[i],
            name=f"Availability_{i}"
        )

    # Demand constraints
    for j in range(num_routes):
        model.addConstr(
            gp.quicksum(capabilities[i][j] * x[i, j] for i in range(num_aircraft)) >= demand[j],
            name=f"Demand_{j}"
        )

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        total_cost = model.objVal
        return total_cost
    else:
        return None

if __name__ == "__main__":
    result = aircraft_assignment()
    print(f"Minimum total cost: {result}")