import gurobipy as gp
from gurobipy import GRB
import json
import os
machines = list(range(1, 6))  # M = {1, 2, 3, 4, 5}
jobs = list(range(1, 5))  # J = {1, 2, 3, 4}

# JobProcess[j-1] contains a list of tuples (machine, process_time) for job j
job_processes = [
    [(1, 3), (2, 2), (5, 4)],  # Job 1 processes
    [(3, 4), (4, 3), (5, 2)],  # Job 2 processes
    [(2, 3), (1, 5), (4, 2)],  # Job 3 processes
    [(1, 2), (3, 3), (4, 4)]  # Job 4 processes
]

machine_id = ['M1', 'M2', 'M3', 'M4', 'M5']
job_id = ['J1', 'J2', 'J3', 'J4']

def solve_job_shop_scheduling(job_processes=[[(1, 3), (2, 2), (5, 4)], [(3, 4), (4, 3), (5, 2)], [(2, 3), (1, 5), (4, 2)], [(1, 2), (3, 3), (4, 4)]]):
    # Data
    machines = list(range(1, 6))
    jobs = list(range(1, 5))

    # Create a new model
    model = gp.Model("JobShopScheduling")

    # Calculate a big-M value (an upper bound on the makespan)
    big_M = sum(duration for job in job_processes for _, duration in job)

    # Create decision variables
    start_times = {}
    for j in range(len(jobs)):
        for k in range(len(job_processes[j])):
            start_times[j, k] = model.addVar(vtype=GRB.INTEGER,
                                             lb=0,
                                             name=f"StartTime_{j+1}_{k+1}")

    # Create makespan variable
    makespan = model.addVar(vtype=GRB.INTEGER, name="Makespan")

    # Set objective
    model.setObjective(makespan, GRB.MINIMIZE)

    # Constraint 1: The start time of the next process must be greater than or equal to the end time of the previous process
    for j in range(len(jobs)):
        for k in range(len(job_processes[j]) - 1):
            model.addConstr(
                start_times[j,
                            k + 1] >= start_times[j, k] + job_processes[j][k][1],
                f"PrecedenceJob_{j+1}_Process_{k+1}_to_{k+2}")

    # Constraint 2: One machine can only process one job at a time
    for m in machines:
        # Find all processes that use this machine
        processes_on_machine = []
        for j in range(len(jobs)):
            for k in range(len(job_processes[j])):
                if job_processes[j][k][0] == m:
                    processes_on_machine.append((j, k))

        # Add non-overlap constraints for each pair of processes on this machine
        for i in range(len(processes_on_machine)):
            for j in range(i + 1, len(processes_on_machine)):
                j1, k1 = processes_on_machine[i]
                j2, k2 = processes_on_machine[j]

                # Either j1,k1 finishes before j2,k2 starts OR j2,k2 finishes before j1,k1 starts
                indicator = model.addVar(
                    vtype=GRB.BINARY,
                    name=f"Indicator_{j1+1}_{k1+1}_{j2+1}_{k2+1}")
                model.addConstr(
                    start_times[j1, k1] + job_processes[j1][k1][1]
                    <= start_times[j2, k2] + big_M * (1 - indicator),
                    f"NoOverlap1_{j1+1}_{k1+1}_{j2+1}_{k2+1}")
                model.addConstr(
                    start_times[j2, k2] + job_processes[j2][k2][1]
                    <= start_times[j1, k1] + big_M * indicator,
                    f"NoOverlap2_{j1+1}_{k1+1}_{j2+1}_{k2+1}")

    # Constraint 3: The start time of the first process must be greater than or equal to 0
    for j in range(len(jobs)):
        model.addConstr(start_times[j, 0] >= 0, f"NonNegativeStart_{j+1}")

    # Constraint for makespan: makespan is the maximum completion time among all jobs
    for j in range(len(jobs)):
        last_process = len(job_processes[j]) - 1
        model.addConstr(
            makespan
            >= start_times[j, last_process] + job_processes[j][last_process][1],
            f"MakespanDef_{j+1}")

    # Solve the model
    model.optimize()

    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}

if __name__ == "__main__":
    result = solve_job_shop_scheduling()
    print(result)
