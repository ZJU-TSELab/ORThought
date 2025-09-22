import gurobipy as gp
from gurobipy import GRB


def solve_nurse_staffing_with_contract():
    """
    Solves the nurse staffing problem with regular and contract nurses
    to minimize total daily wage costs.
    """
    try:
        # Create a new model
        model = gp.Model("NurseStaffingContract")

        # --- Data ---
        # Demands for each 4-hour period (0 to 5)
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
        # t=0 starts at 2:00, t=1 at 6:00, ..., t=5 at 22:00
        shift_start_times_desc = [
            "2:00", "6:00", "10:00", "14:00", "18:00", "22:00"
        ]

        # Costs
        cost_regular_nurse_shift = 10 * 8  # 10 yuan/hour * 8 hours
        cost_contract_nurse_shift = 15 * 8  # 15 yuan/hour * 8 hours

        # --- Decision Variables ---
        # xR[t]: number of regular nurses starting shift at time t
        xR = model.addVars(num_periods, vtype=GRB.INTEGER, name="xR", lb=0)
        # xC[t]: number of contract nurses starting shift at time t
        xC = model.addVars(num_periods, vtype=GRB.INTEGER, name="xC", lb=0)

        # --- Objective Function ---
        # Minimize the total daily wage cost
        total_cost = gp.quicksum(cost_regular_nurse_shift * xR[t] +
                                 cost_contract_nurse_shift * xC[t]
                                 for t in range(num_periods))
        model.setObjective(total_cost, GRB.MINIMIZE)

        # --- Constraints ---
        # Demand coverage for each period.
        # Each nurse works for 8 hours, covering two 4-hour periods.

        # Period 0 (2:00-6:00): Covered by staff starting at 22:00 (t=5) and 2:00 (t=0)
        model.addConstr((xR[5] + xC[5]) + (xR[0] + xC[0]) >= demands[0],
                        "Demand_P0")

        # Period 1 (6:00-10:00): Covered by staff starting at 2:00 (t=0) and 6:00 (t=1)
        model.addConstr((xR[0] + xC[0]) + (xR[1] + xC[1]) >= demands[1],
                        "Demand_P1")

        # Period 2 (10:00-14:00): Covered by staff starting at 6:00 (t=1) and 10:00 (t=2)
        model.addConstr((xR[1] + xC[1]) + (xR[2] + xC[2]) >= demands[2],
                        "Demand_P2")

        # Period 3 (14:00-18:00): Covered by staff starting at 10:00 (t=2) and 14:00 (t=3)
        model.addConstr((xR[2] + xC[2]) + (xR[3] + xC[3]) >= demands[3],
                        "Demand_P3")

        # Period 4 (18:00-22:00): Covered by staff starting at 14:00 (t=3) and 18:00 (t=4)
        model.addConstr((xR[3] + xC[3]) + (xR[4] + xC[4]) >= demands[4],
                        "Demand_P4")

        # Period 5 (22:00-2:00): Covered by staff starting at 18:00 (t=4) and 22:00 (t=5)
        model.addConstr((xR[4] + xC[4]) + (xR[5] + xC[5]) >= demands[5],
                        "Demand_P5")

        # Suppress Gurobi output to console
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal staffing plan found.")
            print(f"Minimum Total Daily Wage Cost: {model.objVal:.2f} Yuan")

            total_regular_nurses = sum(xR[t].X for t in range(num_periods))
            total_contract_nurses = sum(xC[t].X for t in range(num_periods))

            print(
                f"\nTotal Regular Nurses to Hire: {total_regular_nurses:.0f}")
            print(
                f"Total Contract Nurses to Hire: {total_contract_nurses:.0f}")

            if total_contract_nurses > 0:
                print("\nDecision: The hospital SHOULD hire contract nurses.")
            else:
                print(
                    "\nDecision: The hospital does NOT need to hire contract nurses based on cost minimization."
                )

            print("\nNumber of Nurses Starting at Each Shift:")
            print(f"{'Start Time':<12} | {'Regular':<10} | {'Contract':<10}")
            print("-" * 40)
            for t in range(num_periods):
                print(
                    f"{shift_start_times_desc[t]:<12} | {xR[t].X:<10.0f} | {xC[t].X:<10.0f}"
                )

            print("\nVerification of Coverage per Period:")
            coverage = [0] * num_periods
            coverage[0] = (xR[5].X + xC[5].X) + (xR[0].X + xC[0].X)
            coverage[1] = (xR[0].X + xC[0].X) + (xR[1].X + xC[1].X)
            coverage[2] = (xR[1].X + xC[1].X) + (xR[2].X + xC[2].X)
            coverage[3] = (xR[2].X + xC[2].X) + (xR[3].X + xC[3].X)
            coverage[4] = (xR[3].X + xC[3].X) + (xR[4].X + xC[4].X)
            coverage[5] = (xR[4].X + xC[4].X) + (xR[5].X + xC[5].X)

            period_desc = [
                "2:00-6:00", "6:00-10:00", "10:00-14:00", "14:00-18:00",
                "18:00-22:00", "22:00-2:00"
            ]
            for p in range(num_periods):
                print(
                    f"  Period {period_desc[p]} (Demand: {demands[p]}): Covered by {coverage[p]:.0f} nurses"
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
    solve_nurse_staffing_with_contract()
