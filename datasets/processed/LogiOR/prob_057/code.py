import gurobipy as gp
from gurobipy import GRB


def solve_warehouse_optimization(
    products=[1, 2, 3, 4, 5, 6, 7, 8],
    volume={1: 80, 2: 60, 3: 40, 4: 70, 5: 50, 6: 30, 7: 90, 8: 20},
    profit={
        1: 1200,
        2: 900,
        3: 700,
        4: 1100,
        5: 800,
        6: 500,
        7: 1300,
        8: 300
    },
    warehouse_capacity=500,
    incompatible_pairs=[(1, 3), (1, 5), (2, 4), (3, 1), (3, 6), (4, 2),
                        (4, 7), (5, 1), (6, 3), (7, 4)]
):
    """
    Solves the warehouse storage optimization problem.
    """
    model = gp.Model("Warehouse_Storage_Optimization")

    # Decision Variables
    x = model.addVars(products, vtype=GRB.BINARY, name="select")

    # Objective Function
    model.setObjective(gp.quicksum(profit[p] * x[p] for p in products),
                       GRB.MAXIMIZE)

    # Constraints
    model.addConstr(
        gp.quicksum(volume[p] * x[p] for p in products) <= warehouse_capacity,
        "Capacity")

    for (p, q) in incompatible_pairs:
        model.addConstr(x[p] + x[q] <= 1, f"Incompatible_{p}_{q}")

    # Solve the Model
    model.optimize()

    # Return results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_warehouse_optimization()
    print(result)
