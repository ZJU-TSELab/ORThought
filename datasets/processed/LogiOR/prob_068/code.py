import gurobipy as gp
from gurobipy import GRB


def solve_procurement_problem(
    components=[1, 2, 3, 4, 5],
    suppliers=[1, 2, 3],
    demand={1: 1200, 2: 800, 3: 1500, 4: 900, 5: 600},
    price_data=None,
    reliability={1: 0.85, 2: 0.75, 3: 0.90},
    capacity={1: 2000, 2: 1800, 3: 2500},
    min_reliable_frac=0.6,
    max_spend_frac=0.4
):
    """Solve the supplier procurement optimization problem using Gurobi."""
    if price_data is None:
        price = {
            1: {1: 12, 2: 15, 3: 18, 4: 20, 5: 22},
            2: {1: 14, 2: 16, 3: 17, 4: 19, 5: 21},
            3: {1: 13, 2: 14, 3: 19, 4: 18, 5: 20}
        }
    else:
        price = price_data

    model = gp.Model("ComponentProcurement")

    q = model.addVars(suppliers, components, name="q", lb=0)

    total_cost = gp.quicksum(price[s][c] * q[s, c] for s in suppliers for c in components)
    model.setObjective(total_cost, GRB.MINIMIZE)

    for c in components:
        model.addConstr(gp.quicksum(q[s, c] for s in suppliers) == demand[c])

    for s in suppliers:
        model.addConstr(gp.quicksum(q[s, c] for c in components) <= capacity[s])

    reliable_suppliers = [s for s in suppliers if reliability[s] >= 0.8]
    for c in components:
        model.addConstr(gp.quicksum(q[s, c] for s in reliable_suppliers) >= min_reliable_frac * demand[c])

    total_spend = gp.quicksum(price[s][c] * q[s, c] for s in suppliers for c in components)
    for s in suppliers:
        supplier_spend = gp.quicksum(price[s][c] * q[s, c] for c in components)
        model.addConstr(supplier_spend <= max_spend_frac * total_spend)

    model.optimize()

    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_procurement_problem()
    print(result)
