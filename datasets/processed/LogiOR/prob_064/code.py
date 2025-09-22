import gurobipy as gp
from gurobipy import GRB


def solve_beverage_distribution(
    nodes=['P1', 'P2', 'N1', 'N2', 'N3', 'N4', 'N5', 'S1', 'S2', 'S3'],
    commodities=['Cola', 'Juice', 'Water'],
    arcs_data=[
        ('P1', 'N1', 80, 2), ('P1', 'N2', 60, 3), ('P2', 'N3', 90, 2),
        ('N1', 'N3', 50, 1), ('N2', 'N4', 70, 2), ('N3', 'N5', 100, 3),
        ('N4', 'S1', float('inf'), 1), ('N4', 'S2', float('inf'), 2),
        ('N5', 'S2', float('inf'), 1), ('N5', 'S3', float('inf'), 2)
    ],
    demand={
        'S1': {'Cola': 30, 'Juice': 15, 'Water': 10},
        'S2': {'Cola': 20, 'Juice': 25, 'Water': 15},
        'S3': {'Cola': 10, 'Juice': 5, 'Water': 20}
    },
    supply={
        'P1': {'Cola': 40, 'Juice': 30, 'Water': 20},
        'P2': {'Cola': 30, 'Juice': 25, 'Water': 40}
    }
):
    """Solve the beverage distribution optimization problem using Gurobi."""
    model = gp.Model("BeverageDistribution")

    arcs, capacity, cost = gp.multidict({
        (i, j): [cap, c] for (i, j, cap, c) in arcs_data
    })

    flow = model.addVars(arcs, commodities, lb=0, name="flow")

    model.setObjective(
        gp.quicksum(cost[i, j] * flow[i, j, k] for i, j in arcs for k in commodities),
        GRB.MINIMIZE
    )

    production_nodes = supply.keys()
    demand_nodes = demand.keys()

    for node in nodes:
        for k in commodities:
            net_flow = (flow.sum(node, '*', k) - flow.sum('*', node, k))
            if node in production_nodes:
                model.addConstr(net_flow <= supply[node].get(k, 0))
            elif node in demand_nodes:
                model.addConstr(net_flow == -demand[node].get(k, 0))
            else:
                model.addConstr(net_flow == 0)

    for i, j in arcs:
        if capacity[i, j] != float('inf'):
            model.addConstr(gp.quicksum(flow[i, j, k] for k in commodities) <= capacity[i, j])

    model.optimize()

    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_beverage_distribution()
    print(result)
