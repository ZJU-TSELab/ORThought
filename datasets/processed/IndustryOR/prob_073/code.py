import gurobipy as gp
from gurobipy import GRB


def solve_project_scheduling_cost_minimization():
    """
    Solves the project scheduling problem to minimize total cost,
    including work costs and special machine rental costs.
    """
    try:
        # --- Data ---
        activities = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

        durations = {
            'A': 4,
            'B': 3,
            'C': 5,
            'D': 2,
            'E': 10,
            'F': 10,
            'G': 1
        }  # days

        cost_work_per_day = 1000  # Euros/day
        cost_machine_per_day = 5000  # Euros/day

        # Precedence relationships: predecessor -> successor(s)
        # A -> G, D
        # E, G -> F (meaning F starts after both E and G are complete)
        # D, F -> C
        # F -> B

        # --- Create Gurobi Model ---
        model = gp.Model("ProjectSchedulingCostMinimization")

        # --- Decision Variables ---
        # S[act]: Start time of activity act
        S = model.addVars(activities,
                          name="StartTime",
                          lb=0.0,
                          vtype=GRB.INTEGER)

        # Makespan: Total project duration
        Makespan = model.addVar(name="Makespan", lb=0.0, vtype=GRB.INTEGER)

        # MachineRentalDuration: Duration for which the special machine is rented
        MachineRentalDuration = model.addVar(name="MachineRentalDuration",
                                             lb=0.0,
                                             vtype=GRB.INTEGER)

        # --- Objective Function: Minimize Total Cost ---
        # TotalCost = (CostWorkPerDay * Makespan) + (CostMachinePerDay * MachineRentalDuration)
        objective = cost_work_per_day * Makespan + cost_machine_per_day * MachineRentalDuration
        model.setObjective(objective, GRB.MINIMIZE)

        # --- Constraints ---
        # 1. Precedence Constraints
        # Completion time of activity X is S[X] + durations[X]

        # A -> G
        model.addConstr(S['G'] >= S['A'] + durations['A'], name="Prec_A_G")
        # A -> D
        model.addConstr(S['D'] >= S['A'] + durations['A'], name="Prec_A_D")

        # E -> F
        model.addConstr(S['F'] >= S['E'] + durations['E'], name="Prec_E_F")
        # G -> F
        model.addConstr(S['F'] >= S['G'] + durations['G'], name="Prec_G_F")

        # D -> C
        model.addConstr(S['C'] >= S['D'] + durations['D'], name="Prec_D_C")
        # F -> C
        model.addConstr(S['C'] >= S['F'] + durations['F'], name="Prec_F_C")

        # F -> B
        model.addConstr(S['B'] >= S['F'] + durations['F'], name="Prec_F_B")

        # 2. Makespan Definition
        # Makespan >= Completion time of all final activities (B and C)
        model.addConstr(Makespan >= S['B'] + durations['B'],
                        name="Makespan_vs_B")
        model.addConstr(Makespan >= S['C'] + durations['C'],
                        name="Makespan_vs_C")
        # Also ensure makespan is greater than or equal to completion of any activity
        for act in activities:
            model.addConstr(Makespan >= S[act] + durations[act],
                            name=f"Makespan_vs_{act}")

        # 3. Machine Rental Duration Definition
        # Machine rented from start of A (S['A']) to end of B (S['B'] + durations['B'])
        # MachineRentalDuration >= (Completion Time of B) - (Start Time of A)
        model.addConstr(MachineRentalDuration
                        >= (S['B'] + durations['B']) - S['A'],
                        name="MachineRentalDurationDef")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal project schedule found.")
            print(f"Minimum Total Project Cost: {model.ObjVal:.2f} Euros")
            print(f"  Calculated Makespan: {Makespan.X:.2f} days")
            print(
                f"  Calculated Machine Rental Duration: {MachineRentalDuration.X:.2f} days"
            )

            print("\nActivity Schedule (Start Times):")
            completion_times = {}
            for act in activities:
                completion_times[act] = S[act].X + durations[act]
                print(
                    f"  Activity {act}: Start = {S[act].X:.2f} days, Duration = {durations[act]}, End = {completion_times[act]:.2f} days"
                )

            print("\nCost Breakdown:")
            work_cost = cost_work_per_day * Makespan.X
            machine_cost = cost_machine_per_day * MachineRentalDuration.X
            print(
                f"  Cost of Work (Makespan * {cost_work_per_day}): {work_cost:.2f} Euros"
            )
            print(
                f"  Cost of Machine Rental (RentalDuration * {cost_machine_per_day}): {machine_cost:.2f} Euros"
            )

            # Verify machine rental calculation
            start_A = S['A'].X
            end_B = S['B'].X + durations['B']
            print(
                f"  Machine Rental Period: From start of A ({start_A:.2f}) to end of B ({end_B:.2f})"
            )
            print(
                f"  Calculated duration for rental if positive: {(end_B - start_A):.2f} days"
            )

        elif model.status == GRB.INFEASIBLE:
            print(
                "Model is infeasible. Check precedence constraints or activity durations."
            )
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            # model.computeIIS()
            # model.write("project_scheduling_iis.ilp")
            # print("IIS written to project_scheduling_iis.ilp for debugging.")
        else:
            print(f"Optimization stopped with status: {model.status}")
            if model.SolCount == 0:
                print("No feasible solution found.")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_project_scheduling_cost_minimization()
