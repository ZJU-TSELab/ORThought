def optimize_job_scheduling(jobs=None, machines=None, proces_time=None):
    from gurobipy import Model, GRB, quicksum
    
    # Default data based on the sample
    if jobs is None:
        jobs = [1, 2, 3]
    if machines is None:
        machines = [1, 2]
    if proces_time is None:
        proces_time = [[1, 3], [2, 2], [3, 1]]  # Jobs x Machines
    
    num_jobs = len(jobs)
    num_machines = len(machines)
    
    model = Model("JobScheduling")
    model.setParam('OutputFlag', 0)  # Silence output
    
    # Create variables
    # Start times S_{j,m}
    S = {}
    for j_idx, j in enumerate(jobs):
        for m_idx, m in enumerate(machines):
            S[j, m] = model.addVar(lb=0, name=f"S_{j}_{m}")
    
    # Precedence variables x_{i,j}
    x = {}
    for i_idx, i in enumerate(jobs):
        for j_idx, j in enumerate(jobs):
            if i != j:
                x[i, j] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")
    
    # Auxiliary variable for makespan
    C_max = model.addVar(lb=0, name="C_max")
    
    model.update()
    
    big_M = sum(max(row) for row in proces_time) * 2  # A sufficiently large number
    
    # Constraints
    
    # 1. Job sequence constraints (each job's start times)
    for j_idx, j in enumerate(jobs):
        # First machine start time >= 0
        model.addConstr(S[j, machines[0]] >= 0)
        # Sequential processing on each machine
        for m_idx in range(1, num_machines):
            m_prev = machines[m_idx - 1]
            m_curr = machines[m_idx]
            model.addConstr(
                S[j, m_curr] >= S[j, m_prev] + proces_time[j_idx][m_idx - 1]
            )
    
    # 2. Sequence ordering constraints
    for i_idx, i in enumerate(jobs):
        for j_idx, j in enumerate(jobs):
            if i != j:
                # Each pair must be ordered
                model.addConstr(x[i, j] + x[j, i] == 1)
                for m_idx, m in enumerate(machines):
                    # Enforce precedence based on sequence variables
                    model.addConstr(
                        S[j, m] >= S[i, m] + proces_time[i_idx][m_idx] - big_M * (1 - x[i, j])
                    )
    
    # 3. Define completion times and link to makespan
    for j_idx, j in enumerate(jobs):
        C_jM = S[j, machines[-1]] + proces_time[j_idx][-1]
        model.addConstr(C_jM <= C_max)
    
    # Objective: minimize makespan
    model.setObjective(C_max, GRB.MINIMIZE)
    
    # Optimize
    model.optimize()
    
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
if __name__ == "__main__":
    result = optimize_job_scheduling()
    if result is not None:
        print(f"Minimum makespan: {result}")
    else:
        print("No feasible solution found.")