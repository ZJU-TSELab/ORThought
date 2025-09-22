import gurobipy as gp
from gurobipy import GRB


def solve_lab_scheduling():
    """
    Solves the university computer lab staff scheduling problem
    to minimize total wage costs, subject to various constraints.
    """
    try:
        # --- Data ---
        students_data = {
            1: {
                'wage': 10.0,
                'type': 'undergrad',
                'avail': {
                    'Mon': 6,
                    'Tue': 0,
                    'Wed': 6,
                    'Thu': 0,
                    'Fri': 7
                }
            },
            2: {
                'wage': 10.0,
                'type': 'undergrad',
                'avail': {
                    'Mon': 0,
                    'Tue': 6,
                    'Wed': 0,
                    'Thu': 6,
                    'Fri': 0
                }
            },
            3: {
                'wage': 9.9,
                'type': 'undergrad',
                'avail': {
                    'Mon': 4,
                    'Tue': 8,
                    'Wed': 3,
                    'Thu': 0,
                    'Fri': 5
                }
            },
            4: {
                'wage': 9.8,
                'type': 'undergrad',
                'avail': {
                    'Mon': 5,
                    'Tue': 5,
                    'Wed': 6,
                    'Thu': 0,
                    'Fri': 4
                }
            },
            5: {
                'wage': 10.8,
                'type': 'grad',
                'avail': {
                    'Mon': 3,
                    'Tue': 0,
                    'Wed': 4,
                    'Thu': 8,
                    'Fri': 0
                }
            },
            6: {
                'wage': 11.3,
                'type': 'grad',
                'avail': {
                    'Mon': 0,
                    'Tue': 6,
                    'Wed': 0,
                    'Thu': 6,
                    'Fri': 3
                }
            },
        }
        student_ids = list(students_data.keys())
        undergrad_ids = [
            s for s in student_ids if students_data[s]['type'] == 'undergrad'
        ]
        grad_ids = [
            s for s in student_ids if students_data[s]['type'] == 'grad'
        ]

        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        # Lab operates 8:00 AM to 10:00 PM (22:00) -> 14 hours
        # Hours indexed 0 (8-9am) to 13 (9-10pm)
        hours_of_operation = list(range(14))
        num_op_hours_per_day = len(hours_of_operation)

        # Parameters for constraints
        min_weekly_hours_undergrad = 8
        min_weekly_hours_grad = 7
        max_shifts_per_week_student = 2  # Interpreted as max number of days a student works
        max_students_per_day = 3

        # --- Create Gurobi Model ---
        model = gp.Model("LabStaffScheduling")

        # --- Decision Variables ---
        # x[s,d,h]: 1 if student s works on day d at hour h, 0 otherwise
        x = model.addVars(student_ids,
                          days,
                          hours_of_operation,
                          vtype=GRB.BINARY,
                          name="x")

        # y[s,d]: 1 if student s works on day d, 0 otherwise
        y = model.addVars(student_ids, days, vtype=GRB.BINARY, name="y")

        # --- Objective Function: Minimize Total Wage Cost ---
        total_wage_cost = gp.quicksum(students_data[s]['wage'] * x[s, d, h]
                                      for s in student_ids for d in days
                                      for h in hours_of_operation)
        model.setObjective(total_wage_cost, GRB.MINIMIZE)

        # --- Constraints ---
        # 1. Lab Coverage: Exactly one student on duty per hour
        for d in days:
            for h in hours_of_operation:
                model.addConstr(gp.quicksum(x[s, d, h]
                                            for s in student_ids) == 1,
                                name=f"Coverage_{d}_h{h}")

        # 2. Student Daily Hour Limit
        for s in student_ids:
            for d in days:
                model.addConstr(gp.quicksum(x[s, d, h]
                                            for h in hours_of_operation)
                                <= students_data[s]['avail'][d],
                                name=f"DailyHours_{s}_{d}")

        # 3. Minimum Weekly Hours
        for s in undergrad_ids:
            model.addConstr(gp.quicksum(x[s, d, h] for d in days
                                        for h in hours_of_operation)
                            >= min_weekly_hours_undergrad,
                            name=f"MinWeekly_U_{s}")
        for s in grad_ids:
            model.addConstr(gp.quicksum(x[s, d, h] for d in days
                                        for h in hours_of_operation)
                            >= min_weekly_hours_grad,
                            name=f"MinWeekly_G_{s}")

        # 4. Linking x (hourly assignment) and y (daily work indicator) variables
        for s in student_ids:
            for d in days:
                # If student works any hour on day d, y[s,d] must be 1.
                # (If y[s,d]=0, then sum of x[s,d,h] for that day must be 0)
                model.addConstr(gp.quicksum(x[s, d, h]
                                            for h in hours_of_operation)
                                <= num_op_hours_per_day * y[s, d],
                                name=f"Link_y_upper_{s}_{d}")
                # If y[s,d]=1, student must work at least one hour.
                # (If sum of x[s,d,h] is 0, then y[s,d] must be 0)
                model.addConstr(y[s, d]
                                <= gp.quicksum(x[s, d, h]
                                               for h in hours_of_operation),
                                name=f"Link_y_lower_{s}_{d}")

        # 5. Maximum Shifts (days worked) per Week per Student
        for s in student_ids:
            model.addConstr(gp.quicksum(y[s, d] for d in days)
                            <= max_shifts_per_week_student,
                            name=f"MaxShifts_{s}")

        # 6. Maximum Students per Day
        for d in days:
            model.addConstr(gp.quicksum(y[s, d] for s in student_ids)
                            <= max_students_per_day,
                            name=f"MaxStudentsPerDay_{d}")

        # Optional: Set a time limit for the solver (in seconds)
        # model.setParam('TimeLimit', 120)
        # model.setParam('MIPGap', 0.01) # Relative MIP optimality gap

        # --- Solve the Model ---
        model.optimize()

        # --- Print Results ---
        if model.status == GRB.OPTIMAL or \
           (model.status == GRB.TIME_LIMIT and model.SolCount > 0) or \
           (model.status == GRB.INTERRUPTED and model.SolCount > 0):

            if model.status != GRB.OPTIMAL:
                print(
                    f"--- Optimization stopped with status {model.status}. Displaying best solution found. ---"
                )
            else:
                print("--- Optimal solution found! ---")

            print(f"\nMinimum Total Weekly Wage Cost: {model.ObjVal:.2f} CNY")

            print("\nSchedule Details:")
            for d in days:
                print(f"\n--- {d} ---")
                daily_schedule_str = [""] * num_op_hours_per_day
                students_on_day_d = set()
                for h in hours_of_operation:
                    for s in student_ids:
                        if x[s, d,
                             h].X > 0.5:  # If student s is working at hour h on day d
                            daily_schedule_str[h] = str(s)
                            students_on_day_d.add(s)
                            break  # Move to next hour once student is found

                print(f"  Hourly Assignments (Student ID):")
                for hour_idx, student_on_duty in enumerate(daily_schedule_str):
                    actual_hour = hour_idx + 8  # Convert 0-13 index to 8-21
                    print(
                        f"    {actual_hour:02d}:00 - {actual_hour+1:02d}:00 : Student {student_on_duty if student_on_duty else 'NONE'}"
                    )
                print(
                    f"  Students working on {d}: {sorted(list(students_on_day_d))} (Count: {len(students_on_day_d)})"
                )

            print("\n--- Student Summary ---")
            for s in student_ids:
                total_hours_s = sum(x[s, d, h].X for d in days
                                    for h in hours_of_operation)
                days_worked_s = sum(y[s, d].X for d in days)
                min_req = min_weekly_hours_undergrad if students_data[s][
                    'type'] == 'undergrad' else min_weekly_hours_grad

                print(
                    f"\n  Student {s} ({students_data[s]['type']}, Wage: {students_data[s]['wage']:.2f}):"
                )
                print(
                    f"    Total Hours Worked: {total_hours_s:.0f} (Min Req: {min_req})"
                )
                print(
                    f"    Days Worked (Shifts): {days_worked_s:.0f} (Max Allowed: {max_shifts_per_week_student})"
                )
                print(f"    Daily Availability & Actual Hours:")
                for d in days:
                    actual_daily_hours = sum(x[s, d, h].X
                                             for h in hours_of_operation)
                    print(
                        f"      {d}: Available={students_data[s]['avail'][d]}, Worked={actual_daily_hours:.0f}"
                    )

        elif model.status == GRB.INFEASIBLE:
            print(
                "Model is infeasible. Please check constraints and data for contradictions."
            )
            print(
                "Computing IIS (Irreducible Inconsistent Subsystem) to help debug..."
            )
            model.computeIIS()
            model.write("lab_scheduling_iis.ilp")
            print(
                "IIS written to lab_scheduling_iis.ilp. Review this file to find conflicting constraints."
            )
        elif model.status == GRB.TIME_LIMIT and model.SolCount == 0:
            print("No feasible solution found within the time limit.")
        else:
            print(f"Optimization stopped with status: {model.status}")
            if model.SolCount == 0:
                print("No feasible solution was found.")

    except gp.GurobiError as e:
        print(f"Gurobi Error code {e.errno}: {e}")
    except Exception as e:
        print(f"An Python error occurred: {e}")


if __name__ == '__main__':
    solve_lab_scheduling()
