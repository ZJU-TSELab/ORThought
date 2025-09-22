import gurobipy as gp
from gurobipy import GRB


def solve_factory_production_revised():
    """
    Solves the revised factory production planning problem to maximize profit.
    """
    try:
        # Create a new model
        model = gp.Model("FactoryProductionOptimizationRevised")

        # --- Data ---
        # Processing times (hours/piece)
        proc_times = {
            ('I', 'A1'): 5,
            ('I', 'A2'): 7,
            ('II', 'A1'): 10,
            ('II', 'A2'): 9,
            ('III', 'A2'): 12,
            ('I', 'B1'): 6,
            ('II', 'B1'): 8,
            ('III', 'B2'): 11
        }

        # Effective machine hours (capacity)
        capacities = {'A1': 10000, 'A2': 4000, 'B1': 7000, 'B2': 4000}

        # Operating costs at full capacity (Yuan)
        ocfc = {'A1': 321, 'A2': 250, 'B1': 783, 'B2': 200}

        # Variable operating costs per hour (Yuan/hr)
        # It's good practice to calculate this precisely.
        voc = {
            m: ocfc[m] / capacities[m] if capacities[m] > 0 else 0
            for m in capacities
        }

        # Raw material costs (Yuan/piece)
        rmc = {'I': 0.25, 'II': 0.35, 'III': 0.50}

        # Unit sale prices (Yuan/piece)
        sp = {'I': 1.25, 'II': 2.00, 'III': 2.80}

        products = ['I', 'II', 'III']

        # --- Decision Variables ---
        # X_p: Total pieces of product p to produce
        X = model.addVars(products, name="X", lb=0.0, vtype=GRB.INTEGER)

        # x_pm: Quantity of product p processed on specific machine m, based on allowed routes
        # Process A variables
        x_IA1 = model.addVar(name="x_I_A1", lb=0.0, vtype=GRB.INTEGER)
        x_IA2 = model.addVar(name="x_I_A2", lb=0.0, vtype=GRB.INTEGER)
        x_IIA1 = model.addVar(name="x_II_A1", lb=0.0, vtype=GRB.INTEGER)
        x_IIA2 = model.addVar(name="x_II_A2", lb=0.0, vtype=GRB.INTEGER)
        x_IIIA2 = model.addVar(name="x_III_A2", lb=0.0,
                               vtype=GRB.INTEGER)  # Product III only on A2

        # Process B variables
        x_IB1 = model.addVar(name="x_I_B1", lb=0.0,
                             vtype=GRB.INTEGER)  # Product I only on B1
        x_IIB1 = model.addVar(name="x_II_B1", lb=0.0,
                              vtype=GRB.INTEGER)  # Product II only on B1
        x_IIIB2 = model.addVar(name="x_III_B2", lb=0.0,
                               vtype=GRB.INTEGER)  # Product III only on B2

        # --- Objective Function: Maximize Profit ---
        # Profit = Total Revenue - Total Raw Material Cost - Total Variable Operating Cost

        total_revenue = gp.quicksum(sp[p] * X[p] for p in products)
        total_rmc = gp.quicksum(rmc[p] * X[p] for p in products)

        # Variable operating costs for each machine
        op_cost_A1 = (proc_times[('I', 'A1')] * x_IA1 +
                      proc_times[('II', 'A1')] * x_IIA1) * voc['A1']
        op_cost_A2 = (proc_times[('I', 'A2')] * x_IA2 +
                      proc_times[('II', 'A2')] * x_IIA2 +
                      proc_times[('III', 'A2')] * x_IIIA2) * voc['A2']
        op_cost_B1 = (proc_times[('I', 'B1')] * x_IB1 +
                      proc_times[('II', 'B1')] * x_IIB1) * voc['B1']
        op_cost_B2 = (proc_times[('III', 'B2')] * x_IIIB2) * voc['B2']

        total_variable_op_cost = op_cost_A1 + op_cost_A2 + op_cost_B1 + op_cost_B2

        profit = total_revenue - total_rmc - total_variable_op_cost
        model.setObjective(profit, GRB.MAXIMIZE)

        # --- Constraints ---
        # 1. Machine Capacity Constraints
        model.addConstr(
            proc_times[('I', 'A1')] * x_IA1 + proc_times[('II', 'A1')] * x_IIA1
            <= capacities['A1'], "Cap_A1")
        model.addConstr(
            proc_times[('I', 'A2')] * x_IA2 +
            proc_times[('II', 'A2')] * x_IIA2 +
            proc_times[('III', 'A2')] * x_IIIA2 <= capacities['A2'], "Cap_A2")
        model.addConstr(
            proc_times[('I', 'B1')] * x_IB1 + proc_times[('II', 'B1')] * x_IIB1
            <= capacities['B1'], "Cap_B1")
        model.addConstr(proc_times[('III', 'B2')] * x_IIIB2
                        <= capacities['B2'], "Cap_B2")  # Only Prod III uses B2

        # 2. Production Flow Conservation (linking total product X_p to machine allocations)
        # Product I
        model.addConstr(
            x_IA1 + x_IA2 == X['I'],
            "Flow_I_A_Total")  # Sum of A processing for I = Total I
        model.addConstr(
            x_IB1 == X['I'],
            "Flow_I_B_Total")  # B processing for I (only on B1) = Total I

        # Product II
        model.addConstr(
            x_IIA1 + x_IIA2 == X['II'],
            "Flow_II_A_Total")  # Sum of A processing for II = Total II
        model.addConstr(
            x_IIB1 == X['II'],
            "Flow_II_B_Total")  # B processing for II (only on B1) = Total II

        # Product III
        model.addConstr(x_IIIA2 == X['III'], "Flow_III_A_Total"
                        )  # A processing for III (only on A2) = Total III
        model.addConstr(x_IIIB2 == X['III'], "Flow_III_B_Total"
                        )  # B processing for III (only on B2) = Total III

        # Suppress Gurobi output to console
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal production plan found.")
            print(f"Maximum Profit: {model.objVal:.2f} Yuan")
            print("\nTotal pieces of each product to produce:")
            for p in products:
                print(f"  Product {p}: {X[p].X:.2f} pieces")

            print("\nProduction allocation (pieces on each machine):")
            print("  Process A:")
            if x_IA1.X > 1e-6:
                print(f"    Product I on A1 (x_I_A1): {x_IA1.X:.2f}")
            if x_IA2.X > 1e-6:
                print(f"    Product I on A2 (x_I_A2): {x_IA2.X:.2f}")
            if x_IIA1.X > 1e-6:
                print(f"    Product II on A1 (x_II_A1): {x_IIA1.X:.2f}")
            if x_IIA2.X > 1e-6:
                print(f"    Product II on A2 (x_II_A2): {x_IIA2.X:.2f}")
            if x_IIIA2.X > 1e-6:
                print(f"    Product III on A2 (x_III_A2): {x_IIIA2.X:.2f}")

            print("  Process B:")
            if x_IB1.X > 1e-6:
                print(f"    Product I on B1 (x_I_B1): {x_IB1.X:.2f}")
            if x_IIB1.X > 1e-6:
                print(f"    Product II on B1 (x_II_B1): {x_IIB1.X:.2f}")
            if x_IIIB2.X > 1e-6:
                print(f"    Product III on B2 (x_III_B2): {x_IIIB2.X:.2f}")

            print(
                "\nMachine Utilization (Hours Used / Capacity | % Utilization):"
            )
            hours_A1 = proc_times.get(
                ('I', 'A1'), 0) * x_IA1.X + proc_times.get(
                    ('II', 'A1'), 0) * x_IIA1.X
            hours_A2 = proc_times.get(
                ('I', 'A2'), 0) * x_IA2.X + proc_times.get(
                    ('II', 'A2'), 0) * x_IIA2.X + proc_times.get(
                        ('III', 'A2'), 0) * x_IIIA2.X
            hours_B1 = proc_times.get(
                ('I', 'B1'), 0) * x_IB1.X + proc_times.get(
                    ('II', 'B1'), 0) * x_IIB1.X
            hours_B2 = proc_times.get(('III', 'B2'), 0) * x_IIIB2.X

            util_A1 = (hours_A1 / capacities['A1'] *
                       100) if capacities['A1'] > 0 else 0
            util_A2 = (hours_A2 / capacities['A2'] *
                       100) if capacities['A2'] > 0 else 0
            util_B1 = (hours_B1 / capacities['B1'] *
                       100) if capacities['B1'] > 0 else 0
            util_B2 = (hours_B2 / capacities['B2'] *
                       100) if capacities['B2'] > 0 else 0

            print(
                f"  Machine A1: {hours_A1:.2f} / {capacities['A1']} hours | {util_A1:.1f}%"
            )
            print(
                f"  Machine A2: {hours_A2:.2f} / {capacities['A2']} hours | {util_A2:.1f}%"
            )
            print(
                f"  Machine B1: {hours_B1:.2f} / {capacities['B1']} hours | {util_B1:.1f}%"
            )
            print(
                f"  Machine B2: {hours_B2:.2f} / {capacities['B2']} hours | {util_B2:.1f}%"
            )

        elif model.status == GRB.INFEASIBLE:
            print("Model is infeasible. Check constraints and data.")
            # To help debug, compute and print IIS (Irreducible Inconsistent Subsystem)
            # model.computeIIS()
            # model.write("factory_production_revised_iis.ilp")
            # print("IIS written to factory_production_revised_iis.ilp")
        else:
            print(f"Optimization was stopped with status {model.status}")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_factory_production_revised()
