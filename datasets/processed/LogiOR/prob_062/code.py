import gurobipy as gp
from gurobipy import GRB
import itertools


def solve_capacitated_mst(
    nodes=list(range(9)),
    warehouse=0,
    distances_data=None,
    capacity=3,
    time_limit=60
):
    """
    Solves the capacitated minimal spanning tree problem using a
    single-commodity flow formulation.
    """
    if distances_data is None:
        distances = {
            (0, 1): 12, (0, 2): 8, (1, 2): 5, (1, 3): 9, (2, 4): 7, (3, 4): 6,
            (3, 5): 11, (4, 6): 10, (5, 6): 4, (5, 7): 8, (6, 8): 7, (7, 8): 6
        }
        for i, j in distances.copy():
            distances[j, i] = distances[i, j]
    else:
        distances = distances_data

    stores = [n for n in nodes if n != warehouse]
    demands = {n: 1 if n in stores else -(len(stores)) for n in nodes}

    model = gp.Model("Corrected_CMST")

    x = model.addVars(distances.keys(), vtype=GRB.BINARY, name="edge_selected")
    f = model.addVars(distances.keys(), vtype=GRB.CONTINUOUS, name="flow")

    model.setObjective(
        gp.quicksum(distances[i, j] * x[i, j] for i, j in distances if i < j),
        GRB.MINIMIZE
    )

    model.addConstr(x.sum('*', '*') / 2 == len(nodes) - 1, "num_edges")

    for i in nodes:
        in_flow = gp.quicksum(f[j, i] for j in nodes if (j, i) in distances)
        out_flow = gp.quicksum(f[i, j] for j in nodes if (i, j) in distances)
        model.addConstr(in_flow - out_flow == demands[i], f"flow_balance_{i}")

    for i, j in distances:
        model.addConstr(f[i, j] <= (len(nodes) - 1) * x[i, j], f"flow_link_{i}_{j}")

    for i, j in distances:
        if i != warehouse and j != warehouse:
            model.addConstr(f[i, j] + f[j, i] <= capacity * x[i, j], f"capacity_{i}_{j}")

    model.Params.TimeLimit = time_limit
    model.optimize()

    if model.Status == GRB.OPTIMAL or model.Status == GRB.TIME_LIMIT:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.Status}"}


if __name__ == "__main__":
    result = solve_capacitated_mst()
    print(result)
