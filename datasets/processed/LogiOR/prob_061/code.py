import gurobipy as gp
from gurobipy import GRB


def solve_transportation_problem(
    supply_nodes=['S1', 'S2', 'S3'],
    hub_nodes=['H1', 'H2'],
    demand_nodes=['D1', 'D2', 'D3', 'D4'],
    supply_capacity={'S1': 200, 'S2': 150, 'S3': 180},
    demand_requirement={'D1': 120, 'D2': 90, 'D3': 110, 'D4': 130},
    transport_cost={
        ('S1', 'H1'): 5, ('S1', 'H2'): 7,
        ('S2', 'H1'): 6, ('S2', 'H2'): 8,
        ('S3', 'H1'): 4, ('S3', 'H2'): 5,
        ('H1', 'D1'): 3, ('H1', 'D2'): 4, ('H1', 'D3'): 5, ('H1', 'D4'): 6,
        ('H2', 'D1'): 4, ('H2', 'D2'): 3, ('H2', 'D3'): 6, ('H2', 'D4'): 5,
    }
):
    """Solve the cargo transportation network optimization problem."""
    model = gp.Model("CargoTransportation")

    flow = model.addVars(transport_cost.keys(), lb=0, vtype=GRB.CONTINUOUS, name="flow")

    model.setObjective(
        gp.quicksum(flow[i, j] * transport_cost[i, j] for i, j in transport_cost.keys()),
        GRB.MINIMIZE
    )

    for s in supply_nodes:
        model.addConstr(gp.quicksum(flow[s, h] for h in hub_nodes) <= supply_capacity[s])

    for h in hub_nodes:
        model.addConstr(
            gp.quicksum(flow[s, h] for s in supply_nodes) == gp.quicksum(flow[h, d] for d in demand_nodes)
        )

    for d in demand_nodes:
        model.addConstr(gp.quicksum(flow[h, d] for h in hub_nodes) == demand_requirement[d])

    model.optimize()

    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_transportation_problem()
    print(result)