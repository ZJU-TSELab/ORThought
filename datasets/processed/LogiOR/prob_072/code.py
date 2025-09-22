import gurobipy as gp
from gurobipy import GRB

def solve_warehouse_distribution(
    products=['A', 'B', 'C', 'D', 'E'],
    stores=['Store1', 'Store2', 'Store3'],
    trucks=[1, 2, 3, 4],
    product_weights={'A': 2, 'B': 3, 'C': 1, 'D': 4, 'E': 2},
    truck_capacity=15,
    store_demands={
        'Store1': {'A': 2, 'B': 1, 'C': 3, 'D': 0, 'E': 0},
        'Store2': {'A': 1, 'B': 0, 'C': 0, 'D': 2, 'E': 1},
        'Store3': {'A': 0, 'B': 3, 'C': 2, 'D': 0, 'E': 1}
    }
):
    """
    Solves the warehouse distribution problem using Gurobi.
    Minimizes the number of trucks used to deliver products to stores while meeting demand and capacity constraints.
    """
    # Create model
    model = gp.Model("WarehouseDistribution")

    # Decision variables
    # x[p,s,t]: quantity of product p delivered to store s using truck t
    x = model.addVars(products, stores, trucks, vtype=GRB.INTEGER, name="ProductDelivery")

    # y[t]: binary variable indicating if truck t is used
    y = model.addVars(trucks, vtype=GRB.BINARY, name="TruckUsed")

    # Objective: Minimize total trucks used
    model.setObjective(y.sum(), GRB.MINIMIZE)

    # Constraints
    # 1. Meet all store demands
    for s in stores:
        for p in products:
            model.addConstr(
                gp.quicksum(x[p, s, t] for t in trucks) == store_demands[s][p],
                name=f"Demand_{s}_{p}"
            )

    # 2. Truck capacity limit
    for t in trucks:
        model.addConstr(
            gp.quicksum(product_weights[p] * x[p, s, t] for p in products for s in stores)
            <= truck_capacity * y[t],
            name=f"Capacity_{t}"
        )

    # 3. Logical constraint: if any product is delivered by truck t, y_t must be 1
    # Using a large M (here M = max possible demand for any product)
    M = max(max(demands.values()) for demands in store_demands.values())
    for p in products:
        for s in stores:
            for t in trucks:
                model.addConstr(
                    x[p, s, t] <= M * y[t],
                    name=f"Logic_{p}_{s}_{t}"
                )

    # Solve the model
    model.optimize()

    # Return results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_warehouse_distribution()
    print(result)