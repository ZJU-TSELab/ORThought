import gurobipy as gp
from gurobipy import GRB
from typing import List, Dict, Tuple

def solve_berth_allocation(
    Ships: List[str] = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
    Berths: List[str] = ['B1', 'B2', 'B3'],
    ArrivalTime: Dict[str, int] = {'A': 2, 'B': 5, 'C': 10, 'D': 12, 'E': 18, 'F': 20, 'G': 25, 'H': 30, 'I': 35, 'J': 40},
    OperationTime: Dict[str, int] = {'A': 8, 'B': 10, 'C': 6, 'D': 9, 'E': 7, 'F': 11, 'G': 8, 'H': 12, 'I': 5, 'J': 9},
    Dependencies: List[Tuple[str, str]] = [('A', 'C'), ('D', 'E'), ('B', 'G'), ('H', 'I'), ('G', 'J')],
    MaxTime: int = 72,
    RapidTransshipmentBonus: int = 50000,
    WaitingCost: int = 2000,
    MaxTransshipmentGap: int = 2,
    M: int = 1000
):
    """
    Solves the berth allocation problem using Gurobi.

    Args:
        Ships (List[str]): A list of ship identifiers.
        Berths (List[str]): A list of available berth identifiers.
        ArrivalTime (Dict[str, int]): A dictionary mapping each ship to its Estimated Time of Arrival (ETA) in hours.
        OperationTime (Dict[str, int]): A dictionary mapping each ship to its required service time at the berth in hours.
        Dependencies (List[Tuple[str, str]]): A list of tuples, where each tuple (i, j) means ship i must finish before ship j can start.
        MaxTime (int): The total time window for scheduling, in hours.
        RapidTransshipmentBonus (int): The monetary bonus for achieving a rapid transshipment.
        WaitingCost (int): The cost incurred for each hour a ship waits before service.
        MaxTransshipmentGap (int): The maximum time gap (in hours) between dependent tasks to qualify for the bonus.
        M (int): A sufficiently large number used for "big-M" method in linear programming.
    """
    
    # --- Model Initialization ---
    model = gp.Model("BerthAllocation")

    # --- Decision Variables ---
    # StartTime_i: Start time of service for ship i
    StartTime = model.addVars(Ships, name="StartTime", vtype=GRB.CONTINUOUS, lb=0)
    
    # Assignment_ib: 1 if ship i is assigned to berth b, 0 otherwise
    Assignment = model.addVars(Ships, Berths, name="Assignment", vtype=GRB.BINARY)
    
    # Precedence_ij: 1 if ship i and j are on the same berth and i is first, 0 otherwise
    Precedence = model.addVars(Ships, Ships, name="Precedence", vtype=GRB.BINARY)

    # DependencySatisfaction_p: 1 if precedence pair p=(i,j) gets the bonus, 0 otherwise
    DependencySatisfaction = model.addVars(Dependencies, name="DependencySatisfaction", vtype=GRB.BINARY)

    # W_i: Waiting time for ship i (StartTime_i - ArrivalTime_i)
    w = model.addVars(Ships, name="WaitTime", vtype=GRB.CONTINUOUS, lb=0)


    # --- Objective Function ---
    total_bonus = gp.quicksum(RapidTransshipmentBonus * DependencySatisfaction[p] for p in Dependencies)
    total_waiting_cost = gp.quicksum(WaitingCost * w[i] for i in Ships)

    model.setObjective(total_bonus - total_waiting_cost, GRB.MAXIMIZE)

    # --- Constraints ---
    # Waiting time definition
    model.addConstrs((w[i] == StartTime[i] - ArrivalTime[i] for i in Ships), "DefWaitTime")

    # Constraint 1: Unique berth assignment for each ship
    model.addConstrs((gp.quicksum(Assignment[i, b] for b in Berths) == 1 for i in Ships), "UniqueBerth")

    # Constraint 2: Service must start after ETA
    model.addConstrs((StartTime[i] >= ArrivalTime[i] for i in Ships), "RespectETA")

    # Constraint 3: Service must finish within the planning horizon
    model.addConstrs((StartTime[i] + OperationTime[i] <= MaxTime for i in Ships), "Horizon")

    # Constraint 4: Precedence constraints for dependent ships
    for i, j in Dependencies:
        model.addConstr(StartTime[j] >= StartTime[i] + OperationTime[i], f"Precedence_{i}_{j}")

    # Constraint 5: Berth non-overlapping constraints
    for i in Ships:
        for j in Ships:
            if i == j:
                continue
            for b in Berths:
                # If i and j are on the same berth b, one must precede the other.
                # Precedence_ij + Precedence_ji = 1 if Assignment_ib=1 and Assignment_jb=1
                model.addConstr(Precedence[i, j] + Precedence[j, i] >= Assignment[i, b] + Assignment[j, b] - 1, f"RelativeOrder_{i}_{j}_{b}")

                # If Precedence_ij = 1 (i before j), enforce time separation
                model.addConstr(StartTime[i] + OperationTime[i] <= StartTime[j] + M * (1 - Precedence[i, j]) + M * (2 - Assignment[i, b] - Assignment[j, b]), f"NoOverlap_{i}_before_{j}_on_{b}")

    # Constraint 6: Bonus logic constraints
    for p in Dependencies:
        i, j = p
        # If DependencySatisfaction_p is 1, then the gap must be <= MaxTransshipmentGap.
        # StartTime_j - (StartTime_i + OperationTime_i) <= MaxTransshipmentGap + M * (1 - DependencySatisfaction_p)
        model.addConstr(StartTime[j] - (StartTime[i] + OperationTime[i]) <= MaxTransshipmentGap + M * (1 - DependencySatisfaction[p]), f"BonusLogic_{i}_{j}")


    # --- Solve the Model ---
    model.optimize()

    # --- Return Results ---
    if model.Status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.Status}"}


if __name__ == "__main__":
    result = solve_berth_allocation()
    print(result)
