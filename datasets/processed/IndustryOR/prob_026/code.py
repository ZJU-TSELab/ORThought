import gurobipy as gp
from gurobipy import GRB


def solve_factory_production():
    """
    Solves the factory production planning problem to maximize profit.
    """
    try:
        # --- Parameters ---
        # Processing times (hours/unit)
        proc_times = {
            ('I', 'A1'): 5,
            ('I', 'A2'): 7,
            ('II', 'A1'): 10,
            ('II', 'A2'): 9,
            ('III', 'A2'): 12,  # Product III only on A2 for Process A
            ('I', 'B1'): 6,
            ('I', 'B2'): 4,
            ('I', 'B3'): 7,
            ('II', 'B1'): 8,  # Product II only on B1 for Process B
            ('III', 'B2'): 11  # Product III only on B2 for Process B
        }

        # Effective machine hours (capacity)
        capacities = {
            'A1': 6000,
            'A2': 10000,
            'B1': 4000,
            'B2': 7000,
            'B3': 4000
        }

        # Operating costs at full capacity (Yuan)
        ocfc = {'A1': 300, 'A2': 321, 'B1': 250, 'B2': 783, 'B3': 200}

        # Variable operating costs per hour (Yuan/hr)
        voc = {m: ocfc[m] / capacities[m] for m in capacities}

        # Raw material costs (Yuan/unit)
        rmc = {'I': 0.25, 'II': 0.35, 'III': 0.50}

        # Unit sale prices (Yuan/unit)
        sp = {'I': 1.25, 'II': 2.00, 'III': 2.80}

        products = ['I', 'II', 'III']
        machines_A = ['A1', 'A2']
        machines_B = ['B1', 'B2', 'B3']
        all_machines = machines_A + machines_B

        # --- Model Initialization ---
        model = gp.Model("FactoryProductionOptimization")

        # --- Decision Variables ---
        # X_p: Total units of product p to produce
        X = model.addVars(products, name="X", lb=0.0)

        # x_pm: Quantity of product p processed on machine m
        # For Process A machines
        x_IA1 = model.addVar(name="x_I_A1", lb=0.0)
        x_IA2 = model.addVar(name="x_I_A2", lb=0.0)
        x_IIA1 = model.addVar(name="x_II_A1", lb=0.0)
        x_IIA2 = model.addVar(name="x_II_A2", lb=0.0)
        x_IIIA2 = model.addVar(name="x_III_A2", lb=0.0)  # P-III only on A2

        # For Process B machines
        x_IB1 = model.addVar(name="x_I_B1", lb=0.0)
        x_IB2 = model.addVar(name="x_I_B2", lb=0.0)
        x_IB3 = model.addVar(name="x_I_B3", lb=0.0)
        x_IIB1 = model.addVar(name="x_II_B1", lb=0.0)  # P-II only on B1
        x_IIIB2 = model.addVar(name="x_III_B2", lb=0.0)  # P-III only on B2

        # --- Objective Function: Maximize Profit ---
        total_revenue = gp.quicksum(sp[p] * X[p] for p in products)
        total_rmc = gp.quicksum(rmc[p] * X[p] for p in products)

        # Variable operating costs
        op_cost_A1 = (proc_times[('I', 'A1')] * x_IA1 +
                      proc_times[('II', 'A1')] * x_IIA1) * voc['A1']
        op_cost_A2 = (proc_times[('I', 'A2')] * x_IA2 +
                      proc_times[('II', 'A2')] * x_IIA2 +
                      proc_times[('III', 'A2')] * x_IIIA2) * voc['A2']
        op_cost_B1 = (proc_times[('I', 'B1')] * x_IB1 +
                      proc_times[('II', 'B1')] * x_IIB1) * voc['B1']
        op_cost_B2 = (proc_times[('I', 'B2')] * x_IB2 +
                      proc_times[('III', 'B2')] * x_IIIB2) * voc['B2']
        op_cost_B3 = (proc_times[('I', 'B3')] * x_IB3) * voc['B3']

        total_variable_op_cost = op_cost_A1 + op_cost_A2 + op_cost_B1 + op_cost_B2 + op_cost_B3

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
        model.addConstr(
            proc_times[('I', 'B2')] * x_IB2 +
            proc_times[('III', 'B2')] * x_IIIB2 <= capacities['B2'], "Cap_B2")
        model.addConstr(proc_times[('I', 'B3')] * x_IB3 <= capacities['B3'],
                        "Cap_B3")

        # 2. Production Flow Conservation
        # Product I
        model.addConstr(x_IA1 + x_IA2 == X['I'], "Flow_I_A")
        model.addConstr(x_IB1 + x_IB2 + x_IB3 == X['I'], "Flow_I_B")
        # Product II
        model.addConstr(x_IIA1 + x_IIA2 == X['II'], "Flow_II_A")
        model.addConstr(x_IIB1 == X['II'], "Flow_II_B")  # P-II only on B1
        # Product III
        model.addConstr(x_IIIA2 == X['III'], "Flow_III_A")  # P-III only on A2
        model.addConstr(x_IIIB2 == X['III'], "Flow_III_B")  # P-III only on B2

        # --- Optimization ---
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal production plan found.")
            print(f"Maximum Profit: {model.objVal:.2f} Yuan")
            print("\nTotal units of each product to produce:")
            for p in products:
                print(f"  Product {p}: {X[p].X:.2f} units")

            print("\nProduction allocation (units on each machine):")
            print("  Process A:")
            print(f"    Product I on A1 (x_I_A1): {x_IA1.X:.2f}")
            print(f"    Product I on A2 (x_I_A2): {x_IA2.X:.2f}")
            print(f"    Product II on A1 (x_II_A1): {x_IIA1.X:.2f}")
            print(f"    Product II on A2 (x_II_A2): {x_IIA2.X:.2f}")
            print(f"    Product III on A2 (x_III_A2): {x_IIIA2.X:.2f}")
            print("  Process B:")
            print(f"    Product I on B1 (x_I_B1): {x_IB1.X:.2f}")
            print(f"    Product I on B2 (x_I_B2): {x_IB2.X:.2f}")
            print(f"    Product I on B3 (x_I_B3): {x_IB3.X:.2f}")
            print(f"    Product II on B1 (x_II_B1): {x_IIB1.X:.2f}")
            print(f"    Product III on B2 (x_III_B2): {x_IIIB2.X:.2f}")

            print("\nMachine Utilization (Hours Used / Capacity):")
            hours_A1 = proc_times[('I', 'A1')] * x_IA1.X + proc_times[
                ('II', 'A1')] * x_IIA1.X
            hours_A2 = proc_times[('I', 'A2')] * x_IA2.X + proc_times[(
                'II', 'A2')] * x_IIA2.X + proc_times[('III', 'A2')] * x_IIIA2.X
            hours_B1 = proc_times[('I', 'B1')] * x_IB1.X + proc_times[
                ('II', 'B1')] * x_IIB1.X
            hours_B2 = proc_times[('I', 'B2')] * x_IB2.X + proc_times[
                ('III', 'B2')] * x_IIIB2.X
            hours_B3 = proc_times[('I', 'B3')] * x_IB3.X

            print(
                f"  Machine A1: {hours_A1:.2f} / {capacities['A1']} hours ({hours_A1/capacities['A1']*100:.1f}%)"
            )
            print(
                f"  Machine A2: {hours_A2:.2f} / {capacities['A2']} hours ({hours_A2/capacities['A2']*100:.1f}%)"
            )
            print(
                f"  Machine B1: {hours_B1:.2f} / {capacities['B1']} hours ({hours_B1/capacities['B1']*100:.1f}%)"
            )
            print(
                f"  Machine B2: {hours_B2:.2f} / {capacities['B2']} hours ({hours_B2/capacities['B2']*100:.1f}%)"
            )
            print(
                f"  Machine B3: {hours_B3:.2f} / {capacities['B3']} hours ({hours_B3/capacities['B3']*100:.1f}%)"
            )

        elif model.status == GRB.INFEASIBLE:
            print("Model is infeasible. Check constraints and data.")
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            # model.computeIIS()
            # model.write("model_iis.ilp")
            # print("IIS written to model_iis.ilp")
        else:
            print(f"Optimization was stopped with status {model.status}")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    solve_factory_production()
