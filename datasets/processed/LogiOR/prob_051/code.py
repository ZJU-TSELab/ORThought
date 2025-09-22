import gurobipy as gp
from gurobipy import GRB


def solve_assembly_line_balancing(
    tasks=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    duration={
        1: 36, 2: 36, 3: 30, 4: 30, 5: 24,
        6: 30, 7: 24, 8: 12, 9: 54, 10: 12
    },
    precedence=[(1, 2), (1, 5), (2, 7), (3, 4), (4, 5), (5, 6), (6, 8),
                (7, 8), (8, 9), (9, 10)],
    cycle_time=66,
    max_stations=7
):
    """Solve the assembly line balancing problem using Gurobi."""
    # Create a new model
    model = gp.Model("AssemblyLineBalancing")

    workstations = range(1, max_stations + 1)

    # --- Decision Variables ---
    x = model.addVars(tasks, workstations, vtype=GRB.BINARY, name="x")
    y = model.addVars(workstations, vtype=GRB.BINARY, name="y")

    # --- Objective Function ---
    model.setObjective(y.sum(), GRB.MINIMIZE)

    # --- Constraints ---
    model.addConstrs((x.sum(t, '*') == 1 for t in tasks), name="TaskAssignment")
    model.addConstrs((gp.quicksum(duration[t] * x[t, w] for t in tasks) <= cycle_time * y[w]
                      for w in workstations), name="CycleTime")
    model.addConstrs((y[w + 1] <= y[w] for w in workstations if w < max_stations),
                     name="StationSequence")
    for (i, j) in precedence:
        model.addConstr(gp.quicksum(w * x[i, w] for w in workstations)
                        <= gp.quicksum(w * x[j, w] for w in workstations),
                        name=f"Precedence_{i}_{j}")

    # --- Solve the Model ---
    model.optimize()

    # --- Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_assembly_line_balancing()
    print(result)
