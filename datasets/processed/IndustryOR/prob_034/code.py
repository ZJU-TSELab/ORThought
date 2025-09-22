import gurobipy as gp
from gurobipy import GRB


def solve_dyeing_plant_scheduling():
    """
    Solves the dyeing plant scheduling problem to minimize the makespan (completion time of the last batch).
    This is a flow shop scheduling problem.
    """
    try:
        # --- Data ---
        # Processing times p[i][j] for batch i on vat j (hours)
        # Rows: Batches (0 to 4), Columns: Vats (0 to 2)
        processing_times = [
            [3, 1, 1],  # Batch 0
            [2, 1.5, 1],  # Batch 1
            [3, 1.2, 1.3],  # Batch 2
            [2, 2, 2],  # Batch 3
            [2.1, 2, 3]  # Batch 4
        ]

        num_batches = len(processing_times)
        num_vats = len(processing_times[0])

        batches = range(num_batches)
        vats = range(num_vats)

        # Calculate Big-M: Sum of all processing times is a safe upper bound for L
        # and also an upper bound for any start time or makespan.
        L = sum(sum(row)
                for row in processing_times) * 2  # A sufficiently large number

        # --- Create a new model ---
        model = gp.Model("DyeingPlantScheduling")

        # --- Decision Variables ---
        # s[i,j]: start time of batch i on vat j
        s = model.addVars(batches,
                          vats,
                          name="s",
                          lb=0.0,
                          vtype=GRB.CONTINUOUS)

        # C_max: makespan (completion time of the last batch on the last vat)
        C_max = model.addVar(name="C_max", lb=0.0, vtype=GRB.CONTINUOUS)

        # x[i,k,j]: binary variable, 1 if batch i precedes batch k on vat j, 0 otherwise
        # Defined for i < k to avoid redundant pairs
        x = {}
        for j in vats:
            for i in batches:
                for k in batches:
                    if i < k:
                        x[i, k, j] = model.addVar(vtype=GRB.BINARY,
                                                  name=f"x_{i}_{k}_{j}")

        # --- Objective Function ---
        # Minimize the makespan
        model.setObjective(C_max, GRB.MINIMIZE)

        # --- Constraints ---
        # 1. Job Precedence Constraints (operations within the same batch)
        # s_ij >= s_i,(j-1) + p_i,(j-1)
        for i in batches:
            for j in vats:
                if j > 0:  # For vats 1 and 2 (0-indexed)
                    model.addConstr(s[i, j] >= s[i, j - 1] +
                                    processing_times[i][j - 1],
                                    name=f"JobPrecedence_b{i}_v{j}")

        # 2. Machine Capacity Constraints (Disjunctive constraints for operations on the same vat)
        # For each vat j, and for each pair of batches i, k where i < k:
        # s_kj >= s_ij + p_ij - L * (1 - x_ikj)
        # s_ij >= s_kj + p_kj - L * x_ikj
        for j in vats:
            for i in batches:
                for k in batches:
                    if i < k:
                        model.addConstr(s[k, j]
                                        >= s[i, j] + processing_times[i][j] -
                                        L * (1 - x[i, k, j]),
                                        name=f"MachineCap1_v{j}_b{i}_b{k}")
                        model.addConstr(s[i, j]
                                        >= s[k, j] + processing_times[k][j] -
                                        L * x[i, k, j],
                                        name=f"MachineCap2_v{j}_b{i}_b{k}")

        # 3. Makespan Definition
        # C_max >= completion time of batch i on the last vat
        # C_max >= s_i,(M-1) + p_i,(M-1)
        last_vat_idx = num_vats - 1
        for i in batches:
            model.addConstr(C_max >= s[i, last_vat_idx] +
                            processing_times[i][last_vat_idx],
                            name=f"Makespan_b{i}")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)
        model.setParam('MIPGap',
                       0.01)  # Set a MIP gap for faster convergence if needed
        model.setParam('TimeLimit',
                       120)  # Set a time limit (e.g., 120 seconds)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT and model.SolCount > 0:
            if model.status == GRB.TIME_LIMIT:
                print(
                    "Optimal solution not found within time limit. Displaying best solution found."
                )
            else:
                print("Optimal solution found.")

            print(f"\nMinimum Makespan (C_max): {C_max.X:.2f} hours")

            print("\nSchedule (Start Times s_ij):")
            for i in batches:
                print(f"  Batch {i+1}:")
                for j in vats:
                    completion_time = s[i, j].X + processing_times[i][j]
                    print(
                        f"    Vat {j+1}: Start = {s[i,j].X:.2f}, End = {completion_time:.2f} (Duration: {processing_times[i][j]})"
                    )

            print("\nSequence on Vats (derived from start times):")
            for j in vats:
                vat_schedule = []
                for i in batches:
                    vat_schedule.append({
                        'batch': i + 1,
                        'start_time': s[i, j].X,
                        'proc_time': processing_times[i][j]
                    })

                # Sort batches by start time on this vat
                vat_schedule.sort(key=lambda e: e['start_time'])

                sequence_str = " -> ".join([
                    f"B{e['batch']}({e['start_time']:.2f}-{e['start_time']+e['proc_time']:.2f})"
                    for e in vat_schedule
                ])
                print(f"  Vat {j+1} Sequence: {sequence_str}")

        elif model.status == GRB.INFEASIBLE:
            print("Model is infeasible. Check constraints and data.")
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            # model.computeIIS()
            # model.write("dyeing_plant_iis.ilp")
            # print("IIS written to dyeing_plant_iis.ilp.")
        elif model.status == GRB.TIME_LIMIT and model.SolCount == 0:
            print("No solution found within the time limit.")
        else:
            print(f"Optimization stopped with status: {model.status}")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_dyeing_plant_scheduling()
