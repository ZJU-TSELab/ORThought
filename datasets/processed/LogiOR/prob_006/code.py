import gurobipy as gp
from gurobipy import GRB


def solve_multi_product_transportation(
    warehouse_storage=[
        [600, 900, 750],
        [500, 1500, 1200],
        [800, 1100, 100]
    ],
    location_demand=[
        [200, 400, 300],
        [300, 800, 50],
        [200, 300, 50],
        [75, 250, 80],
        [600, 700, 200],
        [225, 850, 100],
        [300, 200, 200]
    ],
    transportation_cost=[
        [[30, 39, 41], [10, 14, 15], [8, 11, 12], [10, 14, 16], [11, 16, 17], [71, 82, 86], [6, 8, 8]],
        [[22, 27, 29], [7, 9, 9], [10, 12, 13], [7, 9, 9], [21, 26, 28], [82, 95, 99], [13, 17, 18]],
        [[19, 24, 26], [11, 14, 14], [12, 17, 17], [10, 13, 13], [25, 28, 31], [83, 99, 104], [15, 20, 20]]
    ],
    max_one_shipment=625
):
    """
    Models and solves the multi-product transportation problem.
    """
    # --- 1. Model Creation ---
    model = gp.Model("WarehouseTransportation")

    # --- 2. Sets ---
    # Derive sets from the dimensions of the input data
    warehouses = range(len(warehouse_storage))
    locations = range(len(location_demand))
    products = range(len(warehouse_storage[0]))

    # --- 3. Decision Variables ---
    # t[i, j, p] = amount of product p transported from warehouse i to location j
    t = model.addVars(warehouses, locations, products, vtype=GRB.INTEGER, lb=0, name="transport")

    # --- 4. Objective Function ---
    # Minimize total transportation cost
    objective = gp.quicksum(transportation_cost[i][j][p] * t[i, j, p]
                           for i in warehouses
                           for j in locations
                           for p in products)
    model.setObjective(objective, GRB.MINIMIZE)

    # --- 5. Constraints ---
    # Constraint 1: Warehouse storage capacity
    for i in warehouses:
        for p in products:
            model.addConstr(gp.quicksum(t[i, j, p] for j in locations) <= warehouse_storage[i][p],
                           name=f"warehouse_capacity_{i+1}_{p+1}")

    # Constraint 2: Sales location demand must be met
    for j in locations:
        for p in products:
            model.addConstr(gp.quicksum(t[i, j, p] for i in warehouses) == location_demand[j][p],
                           name=f"location_demand_{j+1}_{p+1}")

    # Constraint 3: Shipment limit for each warehouse-location pair
    for i in warehouses:
        for j in locations:
            model.addConstr(gp.quicksum(t[i, j, p] for p in products) <= max_one_shipment,
                           name=f"shipment_limit_{i+1}_{j+1}")

    # --- 6. Solve the Model ---
    model.setParam("OutputFlag", 0)  # Suppress Gurobi output
    model.optimize()

    # --- 7. Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        # Return the Gurobi status code if no optimal solution is found
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == "__main__":
    result = solve_multi_product_transportation()
    print(result)