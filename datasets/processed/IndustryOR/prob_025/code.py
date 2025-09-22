import gurobipy as gp
from gurobipy import GRB


def solve_staffing_problem():
    """
    Solves the salespeople staffing problem using Gurobi.
    Minimizes the total number of salespeople required to meet demand
    across different time periods, with 8-hour shifts.
    """
    try:
        # Create a new model
        model = gp.Model("StaffingOptimization")

        # --- Data ---
        # Time periods (start_hour, end_hour) and demand
        # For clarity, let's map period indices to actual start times for variables
        # P0: 2:00-6:00, P1: 6:00-10:00, ..., P5: 22:00-2:00
        demands = {
            0: 10,  # 2:00 - 6:00
            1: 15,  # 6:00 - 10:00
            2: 25,  # 10:00 - 14:00
            3: 20,  # 14:00 - 18:00
            4: 18,  # 18:00 - 22:00
            5: 12  # 22:00 - 2:00 (next day)
        }
        num_periods = len(demands)  # Should be 6

        # Shift start times (represented by an index for variables)
        # x[0] starts at 2:00
        # x[1] starts at 6:00
        # x[2] starts at 10:00
        # x[3] starts at 14:00
        # x[4] starts at 18:00
        # x[5] starts at 22:00
        shift_start_times_desc = [
            "2:00", "6:00", "10:00", "14:00", "18:00", "22:00"
        ]

        # --- Decision Variables ---
        # x[i]: number of salespeople starting their shift at the i-th possible start time
        x = model.addVars(num_periods, vtype=GRB.INTEGER, name="x", lb=0)

        # --- Objective Function ---
        # Minimize the total number of salespeople
        model.setObjective(gp.quicksum(x[i] for i in range(num_periods)),
                           GRB.MINIMIZE)

        # --- Constraints ---
        # Demand coverage for each period.
        # Each salesperson works for 8 hours, covering two 4-hour periods.

        # Period 0 (2:00-6:00): Covered by staff starting at 22:00 (x[5]) and 2:00 (x[0])
        model.addConstr(x[5] + x[0] >= demands[0], "Demand_02_06")

        # Period 1 (6:00-10:00): Covered by staff starting at 2:00 (x[0]) and 6:00 (x[1])
        model.addConstr(x[0] + x[1] >= demands[1], "Demand_06_10")

        # Period 2 (10:00-14:00): Covered by staff starting at 6:00 (x[1]) and 10:00 (x[2])
        model.addConstr(x[1] + x[2] >= demands[2], "Demand_10_14")

        # Period 3 (14:00-18:00): Covered by staff starting at 10:00 (x[2]) and 14:00 (x[3])
        model.addConstr(x[2] + x[3] >= demands[3], "Demand_14_18")

        # Period 4 (18:00-22:00): Covered by staff starting at 14:00 (x[3]) and 18:00 (x[4])
        model.addConstr(x[3] + x[4] >= demands[4], "Demand_18_22")

        # Period 5 (22:00-2:00): Covered by staff starting at 18:00 (x[4]) and 22:00 (x[5])
        model.addConstr(x[4] + x[5] >= demands[5], "Demand_22_02")

        # Suppress Gurobi output to console
        model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal solution found.")
            print(f"Minimum total salespeople needed: {model.objVal:.0f}")
            print("\nNumber of salespeople starting at each shift:")
            for i in range(num_periods):
                print(
                    f"  Start at {shift_start_times_desc[i]}: {x[i].X:.0f} salespeople"
                )

            print("\nVerification of coverage:")
            print(
                f"  Period 2:00-6:00 (Demand: {demands[0]}): Covered by {x[5].X + x[0].X:.0f} (x5={x[5].X:.0f} + x0={x[0].X:.0f})"
            )
            print(
                f"  Period 6:00-10:00 (Demand: {demands[1]}): Covered by {x[0].X + x[1].X:.0f} (x0={x[0].X:.0f} + x1={x[1].X:.0f})"
            )
            print(
                f"  Period 10:00-14:00 (Demand: {demands[2]}): Covered by {x[1].X + x[2].X:.0f} (x1={x[1].X:.0f} + x2={x[2].X:.0f})"
            )
            print(
                f"  Period 14:00-18:00 (Demand: {demands[3]}): Covered by {x[2].X + x[3].X:.0f} (x2={x[2].X:.0f} + x3={x[3].X:.0f})"
            )
            print(
                f"  Period 18:00-22:00 (Demand: {demands[4]}): Covered by {x[3].X + x[4].X:.0f} (x3={x[3].X:.0f} + x4={x[4].X:.0f})"
            )
            print(
                f"  Period 22:00-2:00 (Demand: {demands[5]}): Covered by {x[4].X + x[5].X:.0f} (x4={x[4].X:.0f} + x5={x[5].X:.0f})"
            )

        else:
            print("No optimal solution found. Status code:", model.status)

    except gp.GurobiError as e:
        print(f"Error code {e.errno}: {e}")
    except AttributeError:
        print(
            "Encountered an attribute error, Gurobi might not be installed or licensed correctly."
        )


if __name__ == '__main__':
    solve_staffing_problem()
