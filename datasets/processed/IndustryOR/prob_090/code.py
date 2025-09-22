import gurobipy as gp
from gurobipy import GRB


def solve_new_production_planning():
    """
    Solves a production planning problem with a ratio constraint
    to maximize weekly profit.
    """
    try:
        # --- Parameters ---
        products = ['A', 'B']

        # Profit (£/unit)
        profit = {'A': 3, 'B': 5}

        # Assembly time requirements (minutes/unit)
        assembly_time_req = {'A': 12, 'B': 25}

        # Available assembly time (minutes/week)
        avail_assembly_time = 30 * 60  # 1800 minutes

        # --- Create Gurobi Model ---
        model = gp.Model("NewProductionPlanning")

        # --- Decision Variables ---
        # N[p]: Number of units of product p produced per week
        N = model.addVars(products, name="Produce", vtype=GRB.INTEGER, lb=0)

        # --- Objective Function: Maximize Total Profit ---
        model.setObjective(gp.quicksum(profit[p] * N[p] for p in products),
                           GRB.MAXIMIZE)

        # --- Constraints ---
        # 1. Assembly Time Constraint
        model.addConstr(gp.quicksum(assembly_time_req[p] * N[p]
                                    for p in products) <= avail_assembly_time,
                        name="AssemblyTimeLimit")

        # 2. Technical Ratio Constraint: For every 5 units of A, at least 2 units of B
        # N_B >= (2/5) * N_A  =>  5 * N_B >= 2 * N_A  =>  2 * N_A - 5 * N_B <= 0
        model.addConstr(2 * N['A'] - 5 * N['B'] <= 0, name="RatioConstraint")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal production plan found.")
            print(f"Maximum Weekly Profit: £{model.ObjVal:.2f}")

            print("\nOptimal Production Quantities (units per week):")
            for p in products:
                print(f"  Product {p}: {N[p].X:.0f} units")

            print("\nResource Utilization:")
            assembly_time_used = sum(assembly_time_req[p] * N[p].X
                                     for p in products)
            print(
                f"  Assembly Time Used: {assembly_time_used:.2f} / {avail_assembly_time} minutes "
                f"({(assembly_time_used/avail_assembly_time*100) if avail_assembly_time > 0 else 0:.1f}%)"
            )

            print("\nRatio Constraint Check:")
            ratio_val = (2 * N['A'].X - 5 * N['B'].X)
            print(f"  2*N_A - 5*N_B = {ratio_val:.2f} (Constraint: <= 0)")
            if N['A'].X > 0:
                print(
                    f"  Ratio N_B / N_A = {(N['B'].X / N['A'].X):.3f} (Constraint requires >= 2/5 = 0.4)"
                )
            else:
                print("  Ratio N_B / N_A: N/A (N_A = 0)")

        elif model.status == GRB.INFEASIBLE:
            print("Model is infeasible. Check constraints and requirements.")
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            # model.computeIIS()
            # model.write("new_production_iis.ilp")
            # print("IIS written to new_production_iis.ilp.")
        else:
            print(f"Optimization stopped with status: {model.status}")
            if model.SolCount == 0:
                print("No feasible solution found.")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_new_production_planning()
