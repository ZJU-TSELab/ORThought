import gurobipy as gp
from gurobipy import GRB


def solve_task_assignment(
    complete_time=[
        [5, 2, 3, 15, 9, 10],
        [5, 6, 15, 2, 4, 7],
        [15, 5, 14, 7, 15, 6],
        [20, 15, 18, 6, 8, 11],
        [8, 11, 18, 10, 15, 6],
    ]
):
    """
    Models and solves the task assignment problem.
    """
    # --- 1. Model Creation ---
    model = gp.Model("TaskAssignment")

    # --- 2. Sets ---
    # The number of tasks is the number of rows in complete_time.
    # The number of persons is the number of columns.
    num_tasks = len(complete_time)
    num_persons = len(complete_time[0])
    tasks = range(num_tasks)
    persons = range(num_persons)

    # --- 3. Decision Variables ---
    # x[p, t] = 1 if person p is assigned to task t, 0 otherwise
    x = model.addVars(persons, tasks, vtype=GRB.BINARY, name="assign")

    # --- 4. Objective Function ---
    # Minimize total completion time. Note: complete_time is indexed by [task][person].
    objective = gp.quicksum(complete_time[t][p] * x[p, t]
                           for p in persons for t in tasks)
    model.setObjective(objective, GRB.MINIMIZE)

    # --- 5. Constraints ---
    # Constraint 1: Each person can be assigned to at most one task.
    for p in persons:
        model.addConstr(gp.quicksum(x[p, t] for t in tasks) <= 1,
                        name=f"person_at_most_one_task_{p}")

    # Constraint 2: Each task must be assigned to exactly one person.
    for t in tasks:
        model.addConstr(gp.quicksum(x[p, t] for p in persons) == 1,
                        name=f"task_must_be_assigned_{t}")

    # Constraint 3: Person A (index 0) must be assigned to exactly one task.
    # This makes the general constraint (<=1) redundant for Person A, but is included
    # to match the problem's specific requirements.
    model.addConstr(gp.quicksum(x[0, t] for t in tasks) == 1,
                    name="person_A_must_work")

    # Constraint 4: Person D (index 3) cannot be assigned to task 4 (index 3).
    model.addConstr(x[3, 3] == 0, name="person_D_task_4_restriction")

    # --- 6. Solve the Model ---
    model.setParam("OutputFlag", 0)  # Suppress Gurobi output
    model.optimize()

    # --- 7. Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == "__main__":
    result = solve_task_assignment()
    print(result)
