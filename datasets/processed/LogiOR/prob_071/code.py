import gurobipy as gp
from gurobipy import GRB


def solve_logistics_optimization(
    suppliers=[0, 1, 2],
    warehouses=[0, 1],
    customers=[0, 1, 2, 3],
    supplier_capacities=[120, 150, 90],
    customer_demands=[80, 60, 70, 90],
    direct_cost=[
        [8, 10, 12, 14],  # S1→C1,C2,C3,C4
        [9, 7, 11, 13],  # S2→C1,C2,C3,C4
        [11, 9, 8, 10]  # S3→C1,C2,C3,C4
    ],
    first_leg_cost=[
        [4, 5],  # S1→W1,W2
        [6, 3],  # S2→W1,W2
        [5, 4]  # S3→W1,W2
    ],
    second_leg_cost=[
        [6, 5, 7, 9],  # W1→C1,C2,C3,C4
        [7, 6, 5, 8]  # W2→C1,C2,C3,C4
    ],
    handling_cost=2,
    warehouse_capacities=[200, 180]
):
    """
    Models and solves the logistics optimization problem.
    """
    # Create a new model
    model = gp.Model("LogisticsOptimization")

    # ========== Define Decision Variables ==========
    # Direct shipment variables (supplier → customer)
    direct_ship = model.addVars(suppliers,
                                customers,
                                lb=0.0,
                                vtype=GRB.CONTINUOUS,
                                name="DirectShip")

    # Cross-docking first leg variables (supplier → warehouse)
    cross_dock_first = model.addVars(suppliers,
                                     warehouses,
                                     lb=0.0,
                                     vtype=GRB.CONTINUOUS,
                                     name="CrossDockFirst")

    # Cross-docking second leg variables (warehouse → customer)
    cross_dock_second = model.addVars(warehouses,
                                      customers,
                                      lb=0.0,
                                      vtype=GRB.CONTINUOUS,
                                      name="CrossDockSecond")

    # ========== Set Objective Function ==========
    # Direct shipping cost component
    direct_shipping_cost = gp.quicksum(direct_cost[s][c] *
                                       direct_ship[s, c] for s in suppliers
                                       for c in customers)

    # First leg shipping cost component
    first_leg_shipping_cost = gp.quicksum(
        first_leg_cost[s][w] * cross_dock_first[s, w] for s in suppliers
        for w in warehouses)

    # Second leg shipping cost component
    second_leg_shipping_cost = gp.quicksum(
        second_leg_cost[w][c] * cross_dock_second[w, c] for w in warehouses
        for c in customers)

    # Handling cost component (applied to all cross-docked units)
    handling_cost_total = handling_cost * gp.quicksum(
        cross_dock_second[w, c] for w in warehouses for c in customers)

    # Set objective: minimize total cost
    model.setObjective(
        direct_shipping_cost + first_leg_shipping_cost +
        second_leg_shipping_cost + handling_cost_total, GRB.MINIMIZE)

    # ========== Add Constraints ==========
    # 1. Supplier capacity constraints
    for s in suppliers:
        model.addConstr(gp.quicksum(direct_ship[s, c] for c in customers) +
                        gp.quicksum(cross_dock_first[s, w]
                                    for w in warehouses)
                        <= supplier_capacities[s],
                        name=f"SupplierCapacity_{s}")

    # 2. Customer demand satisfaction
    for c in customers:
        model.addConstr(
            gp.quicksum(direct_ship[s, c] for s in suppliers) +
            gp.quicksum(cross_dock_second[w, c]
                        for w in warehouses) == customer_demands[c],
            name=f"CustomerDemand_{c}")

    # 3. Warehouse flow balance (inflow = outflow)
    for w in warehouses:
        model.addConstr(gp.quicksum(cross_dock_first[s, w]
                                    for s in suppliers) == gp.quicksum(
                                        cross_dock_second[w, c]
                                        for c in customers),
                        name=f"WarehouseFlowBalance_{w}")

    # 4. Warehouse throughput capacity
    for w in warehouses:
        model.addConstr(gp.quicksum(cross_dock_first[s, w]
                                    for s in suppliers)
                        <= warehouse_capacities[w],
                        name=f"WarehouseCapacity_{w}")

    # ========== Solve the Model ==========
    model.optimize()

    # --- 6. Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == "__main__":
    result = solve_logistics_optimization()
    print(result)