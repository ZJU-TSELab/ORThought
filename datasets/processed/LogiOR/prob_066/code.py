import gurobipy as gp
from gurobipy import GRB


def solve_tobacco_distribution(
    centers=['A', 'B', 'C'],
    outlets=list(range(1, 16)),
    capacity={'A': 800, 'B': 600, 'C': 500},
    fixed_cost={'A': 2500, 'B': 2000, 'C': 1800},
    demand=[85, 67, 92, 78, 105, 56, 120, 73, 89, 95, 62, 84, 76, 45, 58],
    max_outlets={'A': 7, 'B': 6, 'C': 5},
    transport_cost_data=None
):
    """
    Solve the multi-depot tobacco distribution network optimization problem.
    """
    if transport_cost_data is None:
        transport_cost = {
            'A': [12, 15, 20, 13, 17, 25, 14, 16, 19, 11, 23, 18, 21, 24, 22],
            'B': [18, 11, 14, 19, 12, 16, 21, 13, 15, 22, 17, 14, 20, 25, 23],
            'C': [22, 25, 16, 23, 20, 14, 18, 24, 17, 19, 15, 21, 13, 16, 12]
        }
    else:
        transport_cost = transport_cost_data

    model = gp.Model("tobacco_distribution")

    x = model.addVars(centers, vtype=GRB.BINARY, name="center_operation")
    y = model.addVars(centers, outlets, vtype=GRB.BINARY, name="assignment")

    fixed_costs = gp.quicksum(fixed_cost[i] * x[i] for i in centers)
    transport_costs = gp.quicksum(
        transport_cost[i][j - 1] * demand[j - 1] * y[i, j]
        for i in centers for j in outlets
    )
    model.setObjective(fixed_costs + transport_costs, GRB.MINIMIZE)

    for j in outlets:
        model.addConstr(gp.quicksum(y[i, j] for i in centers) == 1)

    for i in centers:
        model.addConstr(gp.quicksum(demand[j - 1] * y[i, j] for j in outlets) <= capacity[i] * x[i])
        model.addConstr(gp.quicksum(y[i, j] for j in outlets) <= max_outlets[i] * x[i])
        for j in outlets:
            model.addConstr(y[i, j] <= x[i])

    model.optimize()

    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.objVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_tobacco_distribution()
    print(result)
