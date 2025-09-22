import gurobipy as gp
from gurobipy import GRB


def solve_nonlinear_container_packing(
    container_ids=list(range(6)),
    diameters={0: 1.2, 1: 1.1, 2: 1.0, 3: 0.9, 4: 0.8, 5: 0.7},
    truck_width=2.5,
    time_limit=60
):
    """
    Solves a non-linear container packing problem for a reduced number of containers.
    This model is a Non-Convex Quadratically Constrained Program (QCQP).
    """
    radii = {c: d / 2 for c, d in diameters.items()}

    model = gp.Model("NonlinearContainerPacking")

    x = model.addVars(container_ids, name="x_coord", lb=0.0)
    y = model.addVars(container_ids, name="y_coord", lb=0.0)
    L = model.addVar(name="TruckLength", lb=0.0)

    model.setObjective(L, GRB.MINIMIZE)

    for c in container_ids:
        model.addConstr(y[c] - radii[c] >= 0, name=f"width_lower_{c}")
        model.addConstr(y[c] + radii[c] <= truck_width, name=f"width_upper_{c}")
        model.addConstr(x[c] - radii[c] >= 0, name=f"length_lower_{c}")
        model.addConstr(x[c] + radii[c] <= L, name=f"length_upper_{c}")

    for i in container_ids:
        for j in container_ids:
            if i < j:
                model.addQConstr(
                    (x[i] - x[j]) * (x[i] - x[j]) + (y[i] - y[j]) * (y[i] - y[j]) >= (radii[i] + radii[j])**2,
                    name=f"no_overlap_{i}_{j}"
                )

    model.Params.NonConvex = 2
    model.Params.TimeLimit = time_limit
    
    model.optimize()

    if model.Status == GRB.OPTIMAL or model.Status == GRB.TIME_LIMIT:
        return {"status": "optimal", "obj": L.X}
    else:
        return {"status": f"{model.Status}"}


if __name__ == "__main__":
    result = solve_nonlinear_container_packing()
    print(result)
