import gurobipy as gp
from gurobipy import GRB

def solve_open_shop_scheduling(
    jobs=['C1', 'C2', 'C3', 'C4'],
    machines=['T1', 'T2', 'T3'],
    processing_time={
        'C1': {'T1': 2, 'T2': 3, 'T3': 1},
        'C2': {'T1': 4, 'T2': 2, 'T3': 3},
        'C3': {'T1': 1, 'T2': 5, 'T3': 2},
        'C4': {'T1': 3, 'T2': 2, 'T3': 4}
    }
):
    """
    Solves a classic Open Shop Scheduling problem to minimize makespan.
    """
    model = gp.Model("OpenShopScheduling")

    M = sum(processing_time[j][m] for j in jobs for m in machines)

    s = model.addVars(jobs, machines, vtype=GRB.CONTINUOUS, name="start_time")
    C_max = model.addVar(vtype=GRB.CONTINUOUS, name="makespan")
    x = model.addVars(jobs, jobs, machines, vtype=GRB.BINARY, name="machine_sequence")
    y = model.addVars(jobs, machines, machines, vtype=GRB.BINARY, name="job_sequence")

    model.setObjective(C_max, GRB.MINIMIZE)

    for j in jobs:
        for m in machines:
            model.addConstr(s[j, m] + processing_time[j][m] <= C_max, f"makespan_{j}_{m}")

        for m1_idx, m1 in enumerate(machines):
            for m2_idx, m2 in enumerate(machines):
                if m1_idx < m2_idx:
                    model.addConstr(
                        s[j, m1] + processing_time[j][m1] <= s[j, m2] + M * (1 - y[j, m1, m2]),
                        f"job_non_overlap1_{j}_{m1}_{m2}")
                    model.addConstr(
                        s[j, m2] + processing_time[j][m2] <= s[j, m1] + M * y[j, m1, m2],
                        f"job_non_overlap2_{j}_{m1}_{m2}")

    for m in machines:
        for j1_idx, j1 in enumerate(jobs):
            for j2_idx, j2 in enumerate(jobs):
                if j1_idx < j2_idx:
                    model.addConstr(
                        s[j1, m] + processing_time[j1][m] <= s[j2, m] + M * (1 - x[j1, j2, m]),
                        f"machine_non_overlap1_{j1}_{j2}_{m}")
                    model.addConstr(
                        s[j2, m] + processing_time[j2][m] <= s[j1, m] + M * x[j1, j2, m],
                        f"machine_non_overlap2_{j1}_{j2}_{m}")

    model.optimize()

    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}

if __name__ == "__main__":
    result = solve_open_shop_scheduling()
    print(result)
