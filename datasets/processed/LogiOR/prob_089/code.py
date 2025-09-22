import gurobipy as gp
from gurobipy import GRB
from typing import List, Dict, Tuple
import math

def solve_courier_routing(
    Customers: List[int] = [i for i in range(1, 11)],
    Depot: int = 0,
    Positions: Dict[int, Tuple[float, float]] = {
        0: (0, 0), 1: (3, 5), 2: (5, 8), 3: (2, 1), 4: (8, 6), 5: (4, 2), 6: (9, 8), 7: (1, 9), 8: (1, 3), 9: (6, 4), 10: (7, 1)
    },
    ServiceTime: Dict[int, int] = {1: 5, 2: 8, 3: 5, 4: 10, 5: 6, 6: 7, 7: 9, 8: 5, 9: 12, 10: 6, 0: 0},
    TimeWindows: Dict[int, Tuple[str, str]] = {
        1: ("9:30", "10:00"), 2: ("10:00", "10:20"), 3: ("9:00", "9:20"),
        4: ("10:30", "11:00"), 5: ("9:45", "10:15"), 6: ("11:15", "11:40"),
        7: ("10:10", "10:40"), 8: ("9:15", "9:40"), 9: ("10:20", "10:50"),
        10: ("11:00", "11:20")
    },
    DepartureTimeStr: str = "8:30",
    TravelSpeed_kmh: float = 30.0,
    TravelCostRate_per_km: float = 5.0,
    PenaltyCoefficient: float = 0.2
):
    """
    Solves the courier routing problem with soft time windows and a quadratic penalty function.
    This version includes corrections for sub-tour elimination.
    """
    # --- Data Pre-processing ---
    Locations = [Depot] + Customers
    
    def time_to_minutes(t_str: str) -> int:
        h, m = map(int, t_str.split(':'))
        return h * 60 + m

    DepartureTime = time_to_minutes(DepartureTimeStr)
    TimeWindowCenter = {
        c: (time_to_minutes(tw[0]) + time_to_minutes(tw[1])) / 2
        for c, tw in TimeWindows.items()
    }

    def euclidean_distance(p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    Distances = {
        (i, j): euclidean_distance(Positions[i], Positions[j])
        for i in Locations for j in Locations if i != j
    }
    
    TravelTimes = {
        (i, j): (Distances[i, j] / TravelSpeed_kmh) * 60
        for i, j in Distances
    }
    
    # A large number for Big-M constraints
    M = 24 * 60 # Max minutes in a day

    # --- Model Initialization ---
    model = gp.Model("CourierRoutingWithTimeWindows")

    # --- Decision Variables ---
    x = model.addVars(Locations, Locations, name="Path", vtype=GRB.BINARY)
    t = model.addVars(Locations, name="ArrivalTime", vtype=GRB.CONTINUOUS, lb=0)
    u = model.addVars(Locations, name="Sequence", vtype=GRB.CONTINUOUS, lb=0)

    # --- Objective Function ---
    travel_cost = gp.quicksum(TravelCostRate_per_km * Distances[i, j] * x[i, j] 
                              for i in Locations for j in Locations if i != j)
    
    penalty_cost = gp.quicksum(PenaltyCoefficient * (t[i] - TimeWindowCenter[i]) * (t[i] - TimeWindowCenter[i])
                               for i in Customers)

    model.setObjective(travel_cost + penalty_cost, GRB.MINIMIZE)

    # --- Constraints ---
    model.addConstrs((x[i, i] == 0 for i in Locations), "NoSelfLoops")
    model.addConstr(gp.quicksum(x[Depot, j] for j in Customers) == 1, "LeaveDepot")
    model.addConstr(gp.quicksum(x[i, Depot] for i in Customers) == 1, "ReturnToDepot")
    model.addConstrs((gp.quicksum(x[i, j] for i in Locations if i != j) == 1 for j in Customers), "EnterCustomerOnce")
    model.addConstrs((gp.quicksum(x[j, i] for i in Locations if i != j) == 1 for j in Customers), "LeaveCustomerOnce")
    model.addConstr(t[Depot] == DepartureTime, "SetDepartureTime")

    # Constraint 5: Time flow constraints 
    for i in Locations:
        for j in Customers:
            if i == j:
                continue
            model.addConstr(t[j] >= t[i] + ServiceTime[i] + TravelTimes[i, j] - M * (1 - x[i, j]), f"TimeFlow_{i}_{j}")
    
    # Constraint 6: Sub-tour elimination (MTZ)
    model.addConstr(u[Depot] == 0, "MTZ_Depot_Start")
    M_u = len(Customers) + 1 # A sufficiently large number for the u sequence

    for i in Locations:
        for j in Customers:
            if i == j:
                continue
            # If courier travels from i to j, then u[j] must be at least u[i] + 1
            model.addConstr(u[j] >= u[i] + 1 - M_u * (1 - x[i, j]), f"MTZ_Flow_{i}_{j}")
    
    # Add bounds on u for customers to strengthen the formulation
    model.addConstrs((u[i] >= 1 for i in Customers), "MTZ_Lower_Bound")
    model.addConstrs((u[i] <= len(Customers) for i in Customers), "MTZ_Upper_Bound")
    
    # --- Solve the Model ---
    model.optimize()

    # --- Return Results ---
    if model.Status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.Status}"}


if __name__ == "__main__":
    result = solve_courier_routing()
    print(result)
