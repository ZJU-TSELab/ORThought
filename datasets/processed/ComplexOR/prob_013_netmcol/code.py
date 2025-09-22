def optimize_transportation(
    Cities=['A', 'B'],
    Links=[['A', 'B']],
    Products=['Product1'],
    Supply=[[10], [0]],
    Demand=[[0], [10]],
    ShipmentCost=[[[0], [1]], [[0], [0]]],
    Capacity=[[[0], [10]], [[0], [0]]],
    JointCapacity=[[0, 10], [0, 0]],
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create model
    model = gp.Model("Transportation_Problem")
    model.Params.OutputFlag = 0  # Suppress output

    # Map city and product indices for convenience
    city_indices = {city: idx for idx, city in enumerate(Cities)}
    product_indices = {prod: idx for idx, prod in enumerate(Products)}

    # Decision variables: x[i,j,p]
    x = {}
    for i, city_i in enumerate(Cities):
        for j, city_j in enumerate(Cities):
            for p, prod in enumerate(Products):
                var_name = f"x_{city_i}_{city_j}_{prod}"
                cap = Capacity[i][j][p]
                # Only create variables where capacity > 0
                if cap > 0:
                    x[i, j, p] = model.addVar(lb=0, ub=cap, name=var_name)
                else:
                    # If capacity is zero, no shipping possible
                    x[i, j, p] = None

    model.update()

    # Objective: minimize total shipping cost
    obj = gp.LinExpr()
    for (i, j, p), var in x.items():
        if var is not None:
            cost = ShipmentCost[i][j][p]
            obj += cost * var
    model.setObjective(obj, GRB.MINIMIZE)

    # Supply constraints
    for i, city_i in enumerate(Cities):
        for p, prod in enumerate(Products):
            supply_sum = gp.LinExpr()
            for j, city_j in enumerate(Cities):
                var = x.get((i, j, p))
                if var is not None:
                    supply_sum += var
            model.addConstr(supply_sum <= Supply[i][p], name=f"Supply_{city_i}_{prod}")

    # Demand constraints
    for j, city_j in enumerate(Cities):
        for p, prod in enumerate(Products):
            demand_sum = gp.LinExpr()
            for i, city_i in enumerate(Cities):
                var = x.get((i, j, p))
                if var is not None:
                    demand_sum += var
            model.addConstr(demand_sum >= Demand[j][p], name=f"Demand_{city_j}_{prod}")

    # Joint capacity constraints
    for i, city_i in enumerate(Cities):
        for j, city_j in enumerate(Cities):
            joint_cap = JointCapacity[i][j]
            if joint_cap > 0:
                total = gp.LinExpr()
                for p, prod in enumerate(Products):
                    var = x.get((i, j, p))
                    if var is not None:
                        total += var
                model.addConstr(total <= joint_cap, name=f"JointCap_{city_i}_{city_j}")

    # Optimize
    model.optimize()

    # Return the optimal objective value if feasible
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None

print(optimize_transportation())