import gurobipy as gp
from gurobipy import GRB


def solve_machine_assignment():
    """
    Solves the machine assignment problem with fixed setup costs and constraints
    to minimize the total cost.
    """
    try:
        # --- Data ---
        parts = list(range(1, 11))  # Parts 1 to 10
        machines = ['A', 'B', 'C']

        # Processing costs c[part][machine]
        # Note: Using part index p-1 for 0-based list access
        processing_costs_data = [
            # A   B    C   (Machine)
            [10, 15, 20],  # Part 1
            [20, 25, 30],  # Part 2
            [30, 35, 40],  # Part 3
            [40, 45, 50],  # Part 4
            [50, 55, 60],  # Part 5
            [60, 65, 70],  # Part 6
            [70, 75, 80],  # Part 7
            [80, 85, 90],  # Part 8
            [90, 95, 100],  # Part 9
            [100, 105, 110]  # Part 10
        ]

        # Create cost dictionary c[p,m] for easier access
        proc_costs = {}
        for p_idx, p in enumerate(parts):
            for m_idx, m in enumerate(machines):
                proc_costs[p, m] = processing_costs_data[p_idx][m_idx]

        # Fixed setup costs d[m]
        setup_costs = {'A': 100, 'B': 135, 'C': 200}

        # --- Create Gurobi Model ---
        model = gp.Model("MachineAssignmentFixedCost")

        # --- Decision Variables ---
        # x[p,m]: 1 if part p is processed on machine m, 0 otherwise
        x = model.addVars(parts, machines, vtype=GRB.BINARY, name="x_assign")

        # y[m]: 1 if machine m is used (setup cost incurred), 0 otherwise
        y = model.addVars(machines, vtype=GRB.BINARY, name="y_setup")

        # --- Objective Function: Minimize Total Cost ---
        total_processing_cost = gp.quicksum(proc_costs[p, m] * x[p, m]
                                            for p in parts for m in machines)
        total_setup_cost = gp.quicksum(setup_costs[m] * y[m] for m in machines)

        model.setObjective(total_processing_cost + total_setup_cost,
                           GRB.MINIMIZE)

        # --- Constraints ---
        # 1. Process Each Part: Each part p processed on exactly one machine m
        for p in parts:
            model.addConstr(gp.quicksum(x[p, m] for m in machines) == 1,
                            name=f"ProcessPart_{p}")

        # 2. Conditional Assignment (Part 1 and Part 2)
        # If x[1,'A'] = 1, then x[2,'B'] + x[2,'C'] = 1
        model.addConstr(x[1, 'A'] <= x[2, 'B'] + x[2, 'C'],
                        name="Cond_1A_implies_2BC")
        # If x[1,'B'] + x[1,'C'] = 1, then x[2,'A'] = 1
        model.addConstr(x[1, 'B'] + x[1, 'C'] <= x[2, 'A'],
                        name="Cond_1BC_implies_2A")

        # 3. Fixed Assignments (Parts 3, 4, 5)
        model.addConstr(x[3, 'A'] == 1, name="Fixed_Part3_MachineA")
        model.addConstr(x[4, 'B'] == 1, name="Fixed_Part4_MachineB")
        model.addConstr(x[5, 'C'] == 1, name="Fixed_Part5_MachineC")

        # 4. Machine C Capacity Limit: No more than 3 parts on machine C
        model.addConstr(gp.quicksum(x[p, 'C'] for p in parts) <= 3,
                        name="Limit_MachineC")

        # 5. Linking Setup Cost: If any x[p,m] = 1, then y[m] must be 1
        for m in machines:
            for p in parts:
                model.addConstr(x[p, m] <= y[m], name=f"LinkSetup_{p}_{m}")

        # Alternative tighter linking constraint (optional, usually the one above is sufficient)
        # for m in machines:
        #     model.addConstr(gp.quicksum(x[p,m] for p in parts) <= len(parts) * y[m],
        #                     name=f"LinkSetupAggregate_{m}")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal assignment found.")
            print(
                f"Minimum Total Cost (Processing + Setup): {model.ObjVal:.2f} Yuan"
            )

            print("\nMachine Setup Status:")
            for m in machines:
                if y[m].X > 0.5:
                    print(
                        f"  Machine {m}: Used (Setup Cost: {setup_costs[m]})")
                else:
                    print(f"  Machine {m}: Not Used")

            print("\nPart Assignments (Part -> Machine):")
            assignments = {}
            parts_on_machine = {m: [] for m in machines}
            for p in parts:
                for m in machines:
                    if x[p, m].X > 0.5:  # Check if x[p,m] is 1
                        print(
                            f"  Part {p} -> Machine {m} (Processing Cost: {proc_costs[p,m]})"
                        )
                        assignments[p] = m
                        parts_on_machine[m].append(p)
                        break  # Move to next part once assigned

            print("\nParts processed on each machine:")
            for m in machines:
                print(
                    f"  Machine {m}: {sorted(parts_on_machine[m])} (Count: {len(parts_on_machine[m])})"
                )

        elif model.status == GRB.INFEASIBLE:
            print(
                "Model is infeasible. Check constraints and data for contradictions."
            )
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            model.computeIIS()
            model.write("machine_assignment_iis.ilp")
            print(
                "IIS written to machine_assignment_iis.ilp. Review this file to find conflicting constraints."
            )
        else:
            print(f"Optimization stopped with status: {model.status}")
            if model.SolCount == 0:
                print("No feasible solution found.")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_machine_assignment()
