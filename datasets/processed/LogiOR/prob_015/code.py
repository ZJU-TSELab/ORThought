import gurobipy as gp
from gurobipy import GRB

def solve_truck_loading(
    truck_num=12,
    goods_num=100,
    truck_max_capacity_side=[5250, 4750],
    truck_max_weight_difference=500,
    truck_max_thickness=500,
    goods_thickness=[
        108, 62, 121, 31, 37, 90, 49, 49, 53, 156, 37, 62, 85, 78, 110, 119, 58,
        159, 62, 150, 97, 131, 88, 89, 146, 50, 69, 58, 106, 138, 105, 95, 131, 38,
        38, 92, 41, 40, 76, 133, 101, 103, 82, 134, 36, 126, 73, 121, 30, 116, 104,
        140, 116, 74, 59, 66, 80, 64, 124, 100, 65, 47, 96, 83, 146, 139, 36, 47,
        58, 133, 93, 60, 41, 38, 105, 31, 119, 115, 98, 93, 37, 90, 121, 83, 92,
        36, 32, 56, 74, 126, 117, 72, 43, 38, 78, 65, 112, 149, 33, 88
    ],
    goods_weight=[
        469, 301, 673, 239, 451, 723, 513, 417, 397, 1715, 261, 578, 916, 736,
        1024, 634, 346, 1038, 428, 1008, 709, 1396, 876, 694, 737, 398, 656, 356,
        1165, 1112, 729, 1070, 1015, 224, 437, 917, 273, 303, 614, 738, 1069, 636,
        686, 1035, 188, 1103, 647, 1269, 271, 1234, 631, 1577, 1201, 614, 435, 564,
        695, 375, 1541, 693, 413, 270, 482, 979, 1461, 1251, 329, 389, 606, 1491,
        445, 493, 357, 403, 706, 196, 1405, 571, 1097, 872, 279, 581, 973, 814,
        585, 221, 235, 664, 817, 929, 951, 509, 434, 339, 525, 499, 1250, 1419,
        140, 720
    ]
):
    """
    Solves the truck loading problem.
    """
    model = gp.Model("TruckLoadingProblem")

    trucks = range(1, truck_num + 1)
    goods = range(1, goods_num + 1)
    sides = [0, 1]

    x = {}
    for g in goods:
        for k in trucks:
            for s in sides:
                x[g, k, s] = model.addVar(vtype=GRB.BINARY, name=f"x_{g}_{k}_{s}")

    y = {}
    for k in trucks:
        y[k] = model.addVar(vtype=GRB.BINARY, name=f"y_{k}")

    objective = gp.quicksum(y[k] for k in trucks)
    model.setObjective(objective, GRB.MINIMIZE)

    for g in goods:
        model.addConstr(gp.quicksum(x[g, k, s] for k in trucks for s in sides) == 1, name=f"good_{g}_assigned_once")

    for k in trucks:
        for s in sides:
            model.addConstr(gp.quicksum(goods_weight[g - 1] * x[g, k, s] for g in goods) <= truck_max_capacity_side[s], name=f"truck_{k}_side_{s}_capacity")

    for k in trucks:
        model.addConstr(gp.quicksum(goods_weight[g - 1] * x[g, k, 0] for g in goods) - gp.quicksum(goods_weight[g - 1] * x[g, k, 1] for g in goods) <= truck_max_weight_difference, name=f"truck_{k}_side_difference_upper")
        model.addConstr(gp.quicksum(goods_weight[g - 1] * x[g, k, 0] for g in goods) - gp.quicksum(goods_weight[g - 1] * x[g, k, 1] for g in goods) >= 0, name=f"truck_{k}_side_difference_lower")

    for k in trucks:
        for s in sides:
            model.addConstr(gp.quicksum(goods_thickness[g - 1] * x[g, k, s] for g in goods) <= truck_max_thickness, name=f"truck_{k}_side_{s}_thickness")

    for k in trucks:
        model.addConstr(gp.quicksum(x[g, k, s] for g in goods for s in sides) >= y[k], name=f"truck_{k}_used_if_loaded_1")

    for g in goods:
        for k in trucks:
            for s in sides:
                model.addConstr(y[k] >= x[g, k, s], name=f"truck_{k}_used_if_loaded_2_{g}_{s}")

    model.optimize()

    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.objVal}
    else:
        return {"status": f"{model.status}"}

if __name__ == "__main__":
    result = solve_truck_loading()
    print(result)
