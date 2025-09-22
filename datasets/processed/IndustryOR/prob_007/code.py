def optimize_worker_task_assignment():
    from gurobipy import Model, GRB

    # Data: hours required for each worker-task pair
    hours = {
        ('I', 'A'): 9,
        ('I', 'B'): 4,
        ('I', 'C'): 3,
        ('I', 'D'): 7,
        ('II', 'A'): 4,
        ('II', 'B'): 6,
        ('II', 'C'): 5,
        ('II', 'D'): 6,
        ('III', 'A'): 5,
        ('III', 'B'): 4,
        ('III', 'C'): 7,
        ('III', 'D'): 5,
        ('IV', 'A'): 7,
        ('IV', 'B'): 5,
        ('IV', 'C'): 2,
        ('IV', 'D'): 3,
        ('V', 'A'): 10,
        ('V', 'B'): 6,
        ('V', 'C'): 7,
        ('V', 'D'): 4
    }

    workers = ['I', 'II', 'III', 'IV', 'V']
    tasks = ['A', 'B', 'C', 'D']

    # Create model
    m = Model("WorkerTaskAssignment")
    m.setParam('OutputFlag', 0)  # Suppress output

    # Decision variables: x_{i,j}
    x = m.addVars(workers, tasks, vtype=GRB.BINARY, name='x')
    # Worker selection variables: y_i
    y = m.addVars(workers, vtype=GRB.BINARY, name='y')

    # Objective: minimize total hours
    m.setObjective(
        sum(hours[(i, j)] * x[i, j] for i in workers for j in tasks),
        GRB.MINIMIZE)

    # Constraints:

    # Each task assigned to exactly one worker
    for j in tasks:
        m.addConstr(sum(x[i, j] for i in workers) == 1,
                    name=f"Task_{j}_assignment")

    # Worker assignment constraints
    for i in workers:
        m.addConstr(sum(x[i, j] for j in tasks) <= y[i],
                    name=f"Worker_{i}_assignment_limit")

    # Exactly 4 workers are selected
    m.addConstr(sum(y[i] for i in workers) == 4, name="Select_4_workers")

    # Linking constraints: worker assigned only if selected
    for i in workers:
        for j in tasks:
            m.addConstr(x[i, j] <= y[i], name=f"Link_{i}_{j}")

    # Optimize
    m.optimize()

    # Check feasibility and return optimal value
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None

if __name__ == "__main__":
    result = optimize_worker_task_assignment()
    if result is not None:
        print(f"Optimal total hours: {result}")
    else:
        print("No feasible solution found.")