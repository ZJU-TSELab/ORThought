import gurobipy as gp
from gurobipy import GRB


def solve_large_scale_transport_problem(
    categories={
        1: "Fruits", 2: "Vegetables", 3: "Dairy", 4: "Meat", 5: "Seafood",
        6: "Baked Goods", 7: "Beverages", 8: "Frozen", 9: "Deli Meats", 10: "Prepared"
    },
    variants=['A', 'B', 'C', 'D', 'E'],
    weight_limit=12.0,
    volume_limit=35.0,
    power_limit=40.0,
    time_limit=100.0,
    bonus_profit=150,
    data={
        1: {'A': [1.1, 2.8, 2.0, 8, 210], 'B': [1.3, 3.2, 2.5, 10, 290], 'C': [0.9, 2.4, 1.8, 7, 190], 'D': [1.4, 3.5, 2.8, 11, 320], 'E': [1.0, 2.6, 1.9, 7.5, 200]},
        2: {'A': [0.8, 2.0, 1.0, 5, 160], 'B': [1.0, 2.5, 1.5, 6, 230], 'C': [0.7, 1.8, 0.9, 4.5, 140], 'D': [1.2, 2.8, 1.8, 7, 260], 'E': [0.9, 2.2, 1.2, 5.5, 190]},
        3: {'A': [1.5, 4.5, 4.2, 12, 360], 'B': [1.3, 4.0, 3.5, 10, 310], 'C': [1.7, 5.0, 4.8, 14, 420], 'D': [1.4, 4.2, 3.8, 11, 340], 'E': [1.6, 4.8, 4.5, 13, 400]},
        4: {'A': [1.9, 4.0, 6.5, 15, 520], 'B': [1.6, 3.5, 5.5, 13, 460], 'C': [2.1, 4.5, 7.2, 17, 580], 'D': [1.8, 3.8, 6.0, 14, 500], 'E': [2.2, 4.8, 7.5, 18, 600]},
        5: {'A': [1.4, 3.0, 8.0, 16, 480], 'B': [1.2, 2.8, 7.0, 14, 430], 'C': [1.6, 3.5, 9.0, 18, 550], 'D': [1.3, 2.9, 7.5, 15, 450], 'E': [1.7, 3.8, 9.5, 19, 590]},
        6: {'A': [0.5, 1.5, 0.5, 2, 90], 'B': [0.7, 2.0, 0.8, 3, 140], 'C': [0.6, 1.8, 0.6, 2.5, 120], 'D': [0.8, 2.2, 1.0, 3.5, 160], 'E': [0.4, 1.2, 0.4, 1.5, 80]},
        7: {'A': [1.8, 3.0, 1.5, 4, 250], 'B': [2.0, 3.5, 1.8, 5, 290], 'C': [1.6, 2.8, 1.4, 3.5, 220], 'D': [2.2, 3.8, 2.0, 6, 330], 'E': [1.7, 2.9, 1.6, 4.5, 240]},
        8: {'A': [2.0, 5.0, 8.0, 20, 500], 'B': [1.8, 4.5, 7.0, 18, 450], 'C': [2.3, 5.5, 9.0, 22, 580], 'D': [2.1, 5.2, 8.5, 21, 540], 'E': [2.5, 6.0, 9.8, 24, 620]},
        9: {'A': [0.9, 2.0, 3.0, 6, 180], 'B': [1.1, 2.5, 3.5, 7, 240], 'C': [0.8, 1.8, 2.8, 5.5, 160], 'D': [1.2, 2.8, 4.0, 8, 270], 'E': [1.0, 2.2, 3.2, 6.5, 210]},
        10: {'A': [1.3, 3.0, 4.0, 9, 300], 'B': [1.5, 3.5, 4.5, 10, 350], 'C': [1.2, 2.8, 3.8, 8, 280], 'D': [1.6, 3.8, 5.0, 11, 380], 'E': [1.4, 3.2, 4.2, 9.5, 330]}
    }
):
    """
    Solves the large-scale, multi-constraint perishable goods
    transportation problem using Gurobi.
    """
    # Create a new model
    model = gp.Model("LargeScalePerishableTransport")

    # --- Decision Variables ---
    x = model.addVars(data.keys(), variants, vtype=GRB.BINARY, name="x")
    y = model.addVar(vtype=GRB.BINARY, name="SynergyBonus")

    # --- Objective Function ---
    base_profit = gp.quicksum(data[c][v][4] * x[c, v] for c in data for v in variants)
    total_profit = base_profit + (bonus_profit * y)
    model.setObjective(total_profit, GRB.MAXIMIZE)

    # --- Constraints ---
    for c in data:
        model.addConstr(gp.quicksum(x[c, v] for v in variants) == 1, name=f"SelectOne_{c}")

    model.addConstr(gp.quicksum(data[c][v][0] * x[c, v] for c in data for v in variants) <= weight_limit, "WeightLimit")
    model.addConstr(gp.quicksum(data[c][v][1] * x[c, v] for c in data for v in variants) <= volume_limit, "VolumeLimit")
    model.addConstr(gp.quicksum(data[c][v][2] * x[c, v] for c in data for v in variants) <= power_limit, "PowerLimit")
    model.addConstr(gp.quicksum(data[c][v][3] * x[c, v] for c in data for v in variants) <= time_limit, "TimeLimit")

    model.addConstr(y <= x[1, 'B'], "SynergyCheck1")
    model.addConstr(y <= x[6, 'C'], "SynergyCheck2")
    model.addConstr(y >= x[1, 'B'] + x[6, 'C'] - 1, "SynergyActivation")

    model.addConstr(x[5, 'A'] + x[3, 'A'] <= 1, "ProductConflict")

    # --- Solve ---
    model.optimize()

    # --- Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_large_scale_transport_problem()
    print(result)
