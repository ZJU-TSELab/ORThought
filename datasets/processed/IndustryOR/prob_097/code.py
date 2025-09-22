import gurobipy as gp
from gurobipy import GRB


def solve_production_planning_with_overtime():
    """
    Solves the production planning problem to maximize net profit,
    considering resource constraints and overtime pay.
    """
    try:
        # --- Parameters ---
        products = ['A', 'B']

        # Profit per unit (excluding worker overtime pay) (yuan/unit)
        gross_profit = {'A': 5000, 'B': 11000}

        # Resource requirements per unit
        steel_req = {'A': 6, 'B': 12}  # kg/unit
        aluminum_req = {'A': 8, 'B': 20}  # kg/unit
        labor_req = {'A': 11, 'B': 24}  # hours/unit

        # Resource availability
        avail_steel = 200  # kg
        avail_aluminum = 300  # kg
        avail_labor_regular = 300  # hours

        # Overtime pay (yuan/hour)
        overtime_pay_per_hour = 100

        # --- Create Gurobi Model ---
        model = gp.Model("ProductionPlanningOvertime")

        # --- Decision Variables ---
        # X[p]: Number of units of product p to produce
        X = model.addVars(products, name="Produce", vtype=GRB.INTEGER, lb=0)

        # OT: Total overtime hours used
        OT = model.addVar(name="OvertimeHours", lb=0.0, vtype=GRB.CONTINUOUS)

        # --- Objective Function: Maximize Net Profit ---
        # Net Profit = Gross Profit from Products - Cost of Overtime
        total_gross_profit = gp.quicksum(gross_profit[p] * X[p]
                                         for p in products)
        total_overtime_cost = overtime_pay_per_hour * OT

        model.setObjective(total_gross_profit - total_overtime_cost,
                           GRB.MAXIMIZE)

        # --- Constraints ---
        # 1. Steel Constraint
        model.addConstr(gp.quicksum(steel_req[p] * X[p] for p in products)
                        <= avail_steel,
                        name="SteelLimit")

        # 2. Aluminum Constraint
        model.addConstr(gp.quicksum(aluminum_req[p] * X[p] for p in products)
                        <= avail_aluminum,
                        name="AluminumLimit")

        # 3. Labor Constraint
        # Total labor hours required can be met by regular hours + overtime hours
        # TotalLaborRequired <= RegularLaborAvailable + Overtime
        # TotalLaborRequired - Overtime <= RegularLaborAvailable
        total_labor_needed = gp.quicksum(labor_req[p] * X[p] for p in products)
        model.addConstr(total_labor_needed <= avail_labor_regular + OT,
                        name="LaborAvailability")

        # Alternative for Labor Constraint (explicitly defines OT if positive):
        # model.addConstr(total_labor_needed - OT <= avail_labor_regular, name="LaborConstraint")
        # This is equivalent to the one above given OT >= 0.
        # The objective function will naturally try to minimize OT if it costs money.

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal production plan found.")
            print(f"Maximum Net Profit: {model.ObjVal:.2f} Yuan")

            print("\nOptimal Production Quantities (units):")
            for p in products:
                print(f"  Product {p}: {X[p].X:.0f} units")

            print(f"\nOvertime Hours Used: {OT.X:.2f} hours")
            print(
                f"Cost of Overtime: {(overtime_pay_per_hour * OT.X):.2f} Yuan")

            print("\nResource Utilization:")
            steel_used = sum(steel_req[p] * X[p].X for p in products)
            aluminum_used = sum(aluminum_req[p] * X[p].X for p in products)
            labor_needed_val = sum(labor_req[p] * X[p].X for p in products)

            print(
                f"  Steel Used: {steel_used:.2f} / {avail_steel} kg "
                f"({(steel_used/avail_steel*100) if avail_steel > 0 else 0:.1f}%)"
            )
            print(
                f"  Aluminum Used: {aluminum_used:.2f} / {avail_aluminum} kg "
                f"({(aluminum_used/avail_aluminum*100) if avail_aluminum > 0 else 0:.1f}%)"
            )
            print(f"  Total Labor Needed: {labor_needed_val:.2f} hours")
            print(
                f"    Met by Regular Hours: {min(labor_needed_val, avail_labor_regular):.2f} / {avail_labor_regular} hours"
            )
            if OT.X > 1e-6:
                print(f"    Met by Overtime Hours: {OT.X:.2f} hours")

        elif model.status == GRB.INFEASIBLE:
            print(
                "Model is infeasible. Check constraints and resource availability."
            )
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            # model.computeIIS()
            # model.write("production_overtime_iis.ilp")
            # print("IIS written to production_overtime_iis.ilp for debugging.")
        else:
            print(f"Optimization stopped with status: {model.status}")
            if model.SolCount == 0:
                print("No feasible solution found.")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_production_planning_with_overtime()
