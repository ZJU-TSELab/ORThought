import gurobipy as gp
from gurobipy import GRB


def solve_permutation_flow_shop():
    """
    Solves a 3-product, 3-machine permutation flow shop scheduling problem
    to minimize the makespan (total processing cycle).
    """
    try:
        # --- Data ---
        # Processing times: t[product_idx][machine_idx]
        # Product 1 (idx 0), Product 2 (idx 1), Product 3 (idx 2)
        # Machine 1 (idx 0), Machine 2 (idx 1), Machine 3 (idx 2)
        processing_times_data = [
            [2, 3, 1],  # Product 1
            [4, 2, 3],  # Product 2
            [3, 5, 2]  # Product 3
        ]

        num_products = len(processing_times_data)
        num_machines = len(processing_times_data[0])

        products = range(num_products)  # Indices {0, 1, 2}
        machines = range(num_machines)  # Indices {0, 1, 2}
        positions = range(num_products)  # Sequence positions {0, 1, 2}

        # --- Create Gurobi Model ---
        model = gp.Model("PermutationFlowShop")

        # --- Decision Variables ---
        # z[p,k]: 1 if product p is in k-th sequence position, 0 otherwise
        z = model.addVars(products, positions, vtype=GRB.BINARY, name="z")

        # S[k,m]: Start time of the product in k-th sequence position on machine m
        S = model.addVars(positions,
                          machines,
                          vtype=GRB.CONTINUOUS,
                          name="S",
                          lb=0.0)

        # C_max: Makespan (total processing cycle)
        C_max = model.addVar(vtype=GRB.CONTINUOUS, name="C_max", lb=0.0)

        # --- Objective Function: Minimize Makespan ---
        model.setObjective(C_max, GRB.MINIMIZE)

        # --- Constraints ---
        # 1. Assignment Constraints:
        # Each product p is assigned to exactly one position k
        for p in products:
            model.addConstr(gp.quicksum(z[p, k] for k in positions) == 1,
                            name=f"ProductPos_{p}")

        # Each position k is filled by exactly one product p
        for k in positions:
            model.addConstr(gp.quicksum(z[p, k] for p in products) == 1,
                            name=f"PosProduct_{k}")

        # 2. Scheduling Constraints:
        # PT[k,m] = processing time of product in k-th position on machine m
        # This is not a variable but an expression used in constraints.

        for k in positions:
            for m in machines:
                # Processing time of the job in k-th position on machine m
                pt_km = gp.quicksum(z[p, k] * processing_times_data[p][m]
                                    for p in products)

                # Constraint for job processing sequence (same product, different machines)
                if m > 0:
                    # Processing time of the job in k-th position on machine m-1
                    pt_k_m_minus_1 = gp.quicksum(
                        z[p, k] * processing_times_data[p][m - 1]
                        for p in products)
                    model.addConstr(S[k, m] >= S[k, m - 1] + pt_k_m_minus_1,
                                    name=f"JobSeq_pos{k}_mach{m}")

                # Constraint for machine processing sequence (same machine, different products)
                if k > 0:
                    # Processing time of the job in (k-1)-th position on machine m
                    pt_k_minus_1_m = gp.quicksum(z[p, k - 1] *
                                                 processing_times_data[p][m]
                                                 for p in products)
                    model.addConstr(S[k, m] >= S[k - 1, m] + pt_k_minus_1_m,
                                    name=f"MachSeq_pos{k}_mach{m}")

        # The start time of the first product (position 0) on the first machine (machine 0)
        # S[0,0] >= 0 is already handled by lb=0.0.
        # We can fix it to 0 if desired: S[0,0].ub = 0 or model.addConstr(S[0,0] == 0)

        # 3. Makespan Definition:
        # C_max >= Completion time of the last product (pos N-1) on the last machine (mach NM-1)
        last_pos = num_products - 1
        last_mach = num_machines - 1
        pt_last_job_last_machine = gp.quicksum(
            z[p, last_pos] * processing_times_data[p][last_mach]
            for p in products)
        model.addConstr(C_max
                        >= S[last_pos, last_mach] + pt_last_job_last_machine,
                        name="MakespanDef")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal schedule found.")
            print(
                f"Minimum Total Processing Cycle (Makespan): {C_max.X:.2f} hours"
            )

            print("\nOptimal Product Sequence:")
            optimal_sequence_indices = [0] * num_products
            for p in products:
                for k in positions:
                    if z[p, k].X > 0.5:  # Check if z[p,k] is 1
                        optimal_sequence_indices[
                            k] = p + 1  # Store product number (1-indexed)
            print(" -> ".join(map(str, optimal_sequence_indices)))

            print(
                "\nDetailed Schedule (Start Times S_km for product in k-th position on machine m):"
            )
            print(
                "Pos = Position in Sequence, P# = Product Number, M# = Machine Number"
            )
            for k in positions:
                actual_product_idx = -1
                for p_idx in products:
                    if z[p_idx, k].X > 0.5:
                        actual_product_idx = p_idx
                        break

                print(
                    f"\n  Product at Sequence Position {k+1} (Actual Product {actual_product_idx+1}):"
                )
                for m in machines:
                    pt_val = processing_times_data[actual_product_idx][m]
                    completion_time = S[k, m].X + pt_val
                    print(
                        f"    Machine {m+1}: Start = {S[k,m].X:.2f}, Processing Time = {pt_val:.2f}, Completion = {completion_time:.2f}"
                    )

        elif model.status == GRB.INFEASIBLE:
            print("Model is infeasible. Check constraints and data.")
        else:
            print(f"Optimization stopped with status: {model.status}")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_permutation_flow_shop()
