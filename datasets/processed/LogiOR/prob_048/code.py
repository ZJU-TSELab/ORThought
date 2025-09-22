import gurobipy as gp
from gurobipy import GRB


def solve_supervisor_scheduling(
    operational_hours_needed={
        1: 600, 2: 450, 3: 350, 4: 800, 5: 1000, 6: 450,
        7: 350, 8: 600, 9: 450, 10: 350, 11: 250, 12: 150
    },
    normal_hours_per_supervisor=160,
    overtime_hours_per_supervisor=40,
    supervisors_vacation_months=1,
    fixed_salary=5000,
    overtime_rate=45
):
    """
    Models and solves the supervisor scheduling problem.
    """
    model = gp.Model("WarehouseSupervisors")
    model.setParam('OutputFlag', 0)

    # --- Parameters ---
    months = range(1, 13)

    # --- Decision Variables ---
    supervisors_needed = model.addVar(vtype=GRB.INTEGER, name="SupervisorsNeeded")
    work_supervisor_per_month = model.addVars(months, vtype=GRB.INTEGER, name="WorkSupervisorPerMonth")
    overtime_hours_per_month = model.addVars(months, vtype=GRB.INTEGER, name="OvertimeHoursPerMonth")

    # --- Objective Function ---
    total_cost = fixed_salary * supervisors_needed * 12
    for m in months:
        total_cost += overtime_rate * overtime_hours_per_month[m]
    model.setObjective(total_cost, GRB.MINIMIZE)

    # --- Constraints ---
    for m in months:
        model.addConstr(
            work_supervisor_per_month[m] * normal_hours_per_supervisor +
            overtime_hours_per_month[m] >= operational_hours_needed[m],
            name=f"OperationalHoursNeeded_{m}"
        )

    model.addConstr(
        gp.quicksum(work_supervisor_per_month[m] for m in months) ==
        (12 - supervisors_vacation_months) * supervisors_needed,
        name="VacationConstraint"
    )

    for m in months:
        model.addConstr(
            work_supervisor_per_month[m] <= supervisors_needed,
            name=f"SupervisorsNumberConstraint_{m}"
        )

    for m in months:
        model.addConstr(
            overtime_hours_per_month[m] <= work_supervisor_per_month[m] * overtime_hours_per_supervisor,
            name=f"OvertimeLimit_{m}"
        )

    # --- Solve ---
    model.optimize()

    # --- Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == '__main__':
    result = solve_supervisor_scheduling()
    print(result)