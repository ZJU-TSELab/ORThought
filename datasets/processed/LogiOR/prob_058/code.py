import gurobipy as gp
from gurobipy import GRB


def solve_container_packing(
    parcels=list(range(12)),
    parcel_widths=[30, 25, 40, 15, 35, 20, 25, 30, 15, 20, 10, 25],
    parcel_heights=[40, 35, 20, 25, 30, 15, 20, 25, 10, 30, 15, 10],
    container_width=100,
    M=1000
):
    """Solve the rectangular packing problem to minimize container height."""
    model = gp.Model("ContainerPacking")

    # Create variables
    x = model.addVars(parcels, lb=0, name="x")
    y = model.addVars(parcels, lb=0, name="y")
    a = model.addVars(parcels, parcels, vtype=GRB.BINARY, name="a")
    b = model.addVars(parcels, parcels, vtype=GRB.BINARY, name="b")
    H = model.addVar(lb=0, name="H")

    # Set objective
    model.setObjective(H, GRB.MINIMIZE)

    # Add constraints
    model.addConstrs(
        (x[p] + parcel_widths[p] <= container_width for p in parcels),
        name="width_constraint")

    for p in parcels:
        for q in parcels:
            if p < q:
                model.addConstr(x[p] + parcel_widths[p] <= x[q] + M * (1 - a[p, q]))
                model.addConstr(x[q] + parcel_widths[q] <= x[p] + M * (1 - a[q, p]))
                model.addConstr(y[p] + parcel_heights[p] <= y[q] + M * (1 - b[p, q]))
                model.addConstr(y[q] + parcel_heights[q] <= y[p] + M * (1 - b[q, p]))
                model.addConstr(a[p, q] + a[q, p] + b[p, q] + b[q, p] >= 1)

    model.addConstrs((H >= y[p] + parcel_heights[p] for p in parcels),
                     name="height_calculation")

    # Optimize model
    model.optimize()

    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": H.X}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_container_packing()
    print(result)
