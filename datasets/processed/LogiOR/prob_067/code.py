import gurobipy as gp
from gurobipy import GRB


def solve_hub_location(
    H=[1, 2, 3, 4, 5],
    S=list(range(1, 16)),
    SetupCost={1: 100, 2: 80, 3: 120, 4: 90, 5: 110},
    Capacity={1: 1000, 2: 800, 3: 1500, 4: 1200, 5: 900},
    Reliability={1: 0.85, 2: 0.9, 3: 0.7, 4: 0.95, 5: 0.8},
    TransportCost=0.8,
    MinAvgReliability=0.9,
    Days=365,
    Demand_data=None,
    Distance_data=None
):
    """
    Solve the hub location problem.
    """
    if Demand_data is None:
        Demand = {
            1: 151, 2: 188, 3: 174, 4: 161, 5: 111, 6: 187, 7: 199, 8: 104,
            9: 116, 10: 88, 11: 121, 12: 173, 13: 100, 14: 187, 15: 199
        }
    else:
        Demand = Demand_data

    if Distance_data is None:
        Distance = {
            (1, 1): 18, (1, 2): 45, (1, 3): 42, (1, 4): 38, (1, 5): 18, (1, 6): 44, (1, 7): 47, (1, 8): 12, (1, 9): 20, (1, 10): 10, (1, 11): 23, (1, 12): 41, (1, 13): 10, (1, 14): 44, (1, 15): 47,
            (2, 1): 30, (2, 2): 27, (2, 3): 21, (2, 4): 16, (2, 5): 17, (2, 6): 12, (2, 7): 29, (2, 8): 21, (2, 9): 38, (2, 10): 48, (2, 11): 23, (2, 12): 15, (2, 13): 12, (2, 14): 20, (2, 15): 26,
            (3, 1): 16, (3, 2): 13, (3, 3): 21, (3, 4): 31, (3, 5): 30, (3, 6): 39, (3, 7): 44, (3, 8): 44, (3, 9): 18, (3, 10): 12, (3, 11): 13, (3, 12): 16, (3, 13): 42, (3, 14): 49, (3, 15): 11,
            (4, 1): 34, (4, 2): 25, (4, 3): 30, (4, 4): 20, (4, 5): 24, (4, 6): 28, (4, 7): 42, (4, 8): 39, (4, 9): 31, (4, 10): 44, (4, 11): 34, (4, 12): 11, (4, 13): 36, (4, 14): 16, (4, 15): 23,
            (5, 1): 49, (5, 2): 41, (5, 3): 17, (5, 4): 34, (5, 5): 16, (5, 6): 49, (5, 7): 49, (5, 8): 28, (5, 9): 42, (5, 10): 18, (5, 11): 46, (5, 12): 23, (5, 13): 29, (5, 14): 21, (5, 15): 49
        }
    else:
        Distance = Distance_data

    model = gp.Model("HubLocationProblem")

    OpenHub = model.addVars(H, vtype=GRB.BINARY, name="OpenHub")
    AssignStore = model.addVars(H, S, vtype=GRB.BINARY, name="AssignStore")

    setup_cost = gp.quicksum(SetupCost[h] * 1000 * OpenHub[h] for h in H)
    transport_cost = gp.quicksum(
        TransportCost * Demand[s] * Distance[h, s] * AssignStore[h, s]
        for h in H for s in S
    )
    model.setObjective(Days * (setup_cost + transport_cost), GRB.MINIMIZE)

    model.addConstrs((gp.quicksum(AssignStore[h, s] for h in H) == 1 for s in S))
    model.addConstrs((gp.quicksum(Demand[s] * AssignStore[h, s] for s in S) <= Capacity[h] * OpenHub[h] for h in H))
    model.addConstr(gp.quicksum(Reliability[h] * OpenHub[h] for h in H) >= MinAvgReliability * gp.quicksum(OpenHub[h] for h in H))
    model.addConstrs((AssignStore[h, s] <= OpenHub[h] for h in H for s in S))

    model.optimize()

    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_hub_location()
    print(result)