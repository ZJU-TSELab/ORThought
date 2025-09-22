import gurobipy as gp
from gurobipy import GRB


def solve_logistics_problem(
    orders=list(range(1, 9)),
    trucks=list(range(1, 4)),
    processing_time=[4, 5, 3, 6, 2, 5, 4, 3],
    reentrant_factor=[1, 2, 1, 1, 2, 1, 1, 1],
    truck_capacity=[15, 18, 12],
    operating_cost=[30, 25, 35]
):
    """Solve the truck scheduling problem with reentrant processing requirements."""
    model = gp.Model("LogisticsScheduling")

    x = model.addVars(orders, trucks, vtype=GRB.BINARY, name="Assign")
    y = model.addVars(trucks, vtype=GRB.BINARY, name="TruckUsed")

    model.setObjective(
        gp.quicksum(
            gp.quicksum(
                processing_time[o - 1] * reentrant_factor[o - 1] * x[o, t] * operating_cost[t - 1]
                for o in orders
            )
            for t in trucks
        ),
        GRB.MINIMIZE
    )

    model.addConstrs((gp.quicksum(x[o, t] for t in trucks) == 1 for o in orders))

    model.addConstrs(
        (gp.quicksum(
            processing_time[o - 1] * reentrant_factor[o - 1] * x[o, t]
            for o in orders
        ) <= truck_capacity[t - 1]
        for t in trucks),
        name="Capacity"
    )

    M = len(orders)
    model.addConstrs((gp.quicksum(x[o, t] for o in orders) <= M * y[t] for t in trucks))

    model.optimize()

    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_logistics_problem()
    print(result)
