import gurobipy as gp
from gurobipy import GRB


def solve_bus_staffing():
    """
    Solves the bus service staffing problem to minimize the total number of
    drivers and crew members needed.
    """
    try:
        # Create a new model
        model = gp.Model("BusStaffingOptimization")

        # --- Data ---
        # Demands for each 4-hour period, re-ordered chronologically
        # Period 0: 2:00-6:00 (Original Shift 6)
        # Period 1: 6:00-10:00 (Original Shift 1)
        # Period 2: 10:00-14:00 (Original Shift 2)
        # Period 3: 14:00-18:00 (Original Shift 3)
        # Period 4: 18:00-22:00 (Original Shift 4)
        # Period 5: 22:00-2:00 (Original Shift 5)
        demands = {
            0: 30,  # 2:00 - 6:00
            1: 60,  # 6:00 - 10:00
            2: 70,  # 10:00 - 14:00
            3: 60,  # 14:00 - 18:00
            4: 50,  # 18:00 - 22:00
            5: 20  # 22:00 - 2:00 (next day)
        }
        num_periods = len(demands)  # Should be 6

        # Shift start times descriptions for output
        shift_start_times_desc = [
            "2:00", "6:00", "10:00", "14:00", "18:00", "22:00"
        ]
        period_desc = [
            "2:00-6:00", "6:00-10:00", "10:00-14:00", "14:00-18:00",
            "18:00-22:00", "22:00-2:00"
        ]

        # --- Decision Variables ---
        # x[t]: number of staff starting their 8-hour shift at the beginning of period t
        x = model.addVars(num_periods, vtype=GRB.INTEGER, name="x", lb=0)

        # --- Objective Function ---
        # Minimize the total number of staff members hired
        model.setObjective(gp.quicksum(x[t] for t in range(num_periods)),
                           GRB.MINIMIZE)

        # --- Constraints ---
        # Demand coverage for each period.
        # Each staff member works for 8 hours, covering two 4-hour periods.

        # Period 0 (2:00-6:00): Covered by staff starting at 22:00 (x[5]) and 2:00 (x[0])
        model.addConstr(x[5] + x[0] >= demands[0], "Demand_P0")

        # Period 1 (6:00-10:00): Covered by staff starting at 2:00 (x[0]) and 6:00 (x[1])
        model.addConstr(x[0] + x[1] >= demands[1], "Demand_P1")

        # Period 2 (10:00-14:00): Covered by staff starting at 6:00 (x[1]) and 10:00 (x[2])
        model.addConstr(x[1] + x[2] >= demands[2], "Demand_P2")

        # Period 3 (14:00-18:00): Covered by staff starting at 10:00 (x[2]) and 14:00 (x[3])
        model.addConstr(x[2] + x[3] >= demands[3], "Demand_P3")

        # Period 4 (18:00-22:00): Covered by staff starting at 14:00 (x[3]) and 18:00 (x[4])
        model.addConstr(x[3] + x[4] >= demands[4], "Demand_P4")

        # Period 5 (22:00-2:00): Covered by staff starting at 18:00 (x[4]) and 22:00 (x[5])
        model.addConstr(x[4] + x[5] >= demands[5], "Demand_P5")

        # Suppress Gurobi output to console
        model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal staffing plan found.")
            print(
                f"Minimum total staff (drivers and crew) needed: {model.objVal:.0f}"
            )

            print("\nNumber of Staff Starting at Each Shift:")
            print(f"{'Start Time':<12} | {'Number of Staff':<15}")
            print("-" * 30)
            for t in range(num_periods):
                print(f"{shift_start_times_desc[t]:<12} | {x[t].X:<15.0f}")

            print("\nVerification of Coverage per Period:")
            coverage = [0] * num_periods
            coverage[0] = x[5].X + x[0].X
            coverage[1] = x[0].X + x[1].X
            coverage[2] = x[1].X + x[2].X
            coverage[3] = x[2].X + x[3].X
            coverage[4] = x[3].X + x[4].X
            coverage[5] = x[4].X + x[5].X

            for p_idx in range(num_periods):
                print(
                    f"  Period {period_desc[p_idx]} (Demand: {demands[p_idx]}): Covered by {coverage[p_idx]:.0f} staff"
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
    solve_bus_staffing()
