import gurobipy as gp
from gurobipy import GRB


def solve_workforce_planning_optimization(
    HandleProductPerWorkerPerQuarter=[60, 40],
    WorkerCostPerYear=1800,
    InventoryHoldingCost=70,
    Demand=[[800, 600, 700, 900], [500, 400, 600, 300]]
):
    """
    Models and solves the supply chain logistics and workforce planning problem.
    """
    # Create a new model
    model = gp.Model("SupplyChain_Logistics_Workforce_Planning")

    # Sets
    P = range(len(HandleProductPerWorkerPerQuarter))  # Products
    Q = range(len(Demand[0]))  # Quarters
    G = range(len(Demand[0]))  # Worker Groups

    # Decision Variables
    WorkersInGroup = model.addVars(G, vtype=GRB.INTEGER, lb=0, name="WorkersInGroup")
    ProductProduced = model.addVars(P, Q, vtype=GRB.INTEGER, lb=0, name="ProductProduced")
    ProductStorage = model.addVars(P, Q, vtype=GRB.INTEGER, lb=0, name="ProductStorage")
    WorkersOnDuty = model.addVars(G, P, Q, vtype=GRB.INTEGER, lb=0, name="WorkersOnDuty")

    # Objective Function: Minimize total cost
    labor_cost = gp.quicksum(WorkersInGroup[g] * WorkerCostPerYear for g in G)
    inventory_cost = gp.quicksum(ProductStorage[p, q] * InventoryHoldingCost for p in P for q in Q)
    total_cost = labor_cost + inventory_cost

    model.setObjective(total_cost, GRB.MINIMIZE)

    # Constraints
    # 1. Demand constraints
    for p in P:
        # First quarter (no previous inventory)
        model.addConstr(
            ProductProduced[p, 0] - ProductStorage[p, 0] >= Demand[p][0],
            f"Demand_P{p}_Q1"
        )

        # Subsequent quarters
        for q in range(1, 4):
            model.addConstr(
                ProductProduced[p, q] + ProductStorage[p, q - 1] - ProductStorage[p, q] >= Demand[p][q],
                f"Demand_P{p}_Q{q + 1}"
            )

    # 2. Production handling constraints
    for p in P:
        for q in Q:
            model.addConstr(
                gp.quicksum(WorkersOnDuty[g, p, q] * HandleProductPerWorkerPerQuarter[p] for g in G) >= ProductProduced[p, q],
                f"Production_P{p}_Q{q + 1}"
            )

    # 3. Worker group constraints
    for g in G:
        for q in Q:
            # Workers in group g are off-duty in quarter (g+1)%4
            if q == g:
                # Workers in this group are on leave this quarter
                for p in P:
                    model.addConstr(WorkersOnDuty[g, p, q] == 0, f"OffDuty_G{g + 1}_Q{q + 1}")
            else:
                # Workers on duty can only handle one product type per quarter
                model.addConstr(
                    gp.quicksum(WorkersOnDuty[g, p, q] for p in P) <= WorkersInGroup[g],
                    f"WorkerCapacity_G{g + 1}_Q{q + 1}"
                )

    # 4. End of year inventory must be zero
    for p in P:
        model.addConstr(ProductStorage[p, 3] == 0, f"EndYearInventory_P{p}")

    # Optimize the model
    model.optimize()

    # Return Results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_workforce_planning_optimization()
    print(result)
