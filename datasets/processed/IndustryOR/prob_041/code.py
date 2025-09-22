import gurobipy as gp
from gurobipy import GRB


def solve_steelmaking_allocation():
    """
    Solves the steelmaking allocation problem to minimize fuel expenses
    subject to furnace time and steel production constraints.
    """
    try:
        # --- Parameters ---
        # Method 1
        time_m1 = 2.0  # hours per operation
        cost_m1 = 50.0  # fuel expense per operation

        # Method 2
        time_m2 = 3.0  # hours per operation
        cost_m2 = 70.0  # fuel expense per operation

        # Production
        steel_per_op = 10.0  # tons per operation (same for both methods)

        # Constraints
        min_total_steel = 30.0  # tons
        max_furnace_hours = 12.0  # hours available per furnace

        num_furnaces = 2
        num_methods = 2

        # --- Create Gurobi Model ---
        model = gp.Model("Steelmaking_Allocation")

        # --- Decision Variables ---
        # x[f,m]: number of times furnace f uses method m
        # f=0 for Furnace 1, f=1 for Furnace 2
        # m=0 for Method 1, m=1 for Method 2
        x = model.addVars(num_furnaces,
                          num_methods,
                          name="x",
                          lb=0.0,
                          vtype=GRB.CONTINUOUS)

        # For easier reference using problem's notation:
        # x11 = x[0,0] (Furnace 1, Method 1)
        # x12 = x[0,1] (Furnace 1, Method 2)
        # x21 = x[1,0] (Furnace 2, Method 1)
        # x22 = x[1,1] (Furnace 2, Method 2)

        # --- Objective Function: Minimize Total Fuel Expenses ---
        objective = cost_m1 * (x[0,0] + x[1,0]) + \
                    cost_m2 * (x[0,1] + x[1,1])
        model.setObjective(objective, GRB.MINIMIZE)

        # --- Constraints ---
        # 1. Time Constraint for Furnace 1 (f=0)
        model.addConstr(time_m1 * x[0, 0] + time_m2 * x[0, 1]
                        <= max_furnace_hours,
                        name="Time_Furnace1")

        # 2. Time Constraint for Furnace 2 (f=1)
        model.addConstr(time_m1 * x[1, 0] + time_m2 * x[1, 1]
                        <= max_furnace_hours,
                        name="Time_Furnace2")

        # 3. Steel Production Constraint
        total_steel_produced = steel_per_op * (x[0, 0] + x[0, 1] + x[1, 0] +
                                               x[1, 1])
        model.addConstr(total_steel_produced >= min_total_steel,
                        name="Min_Steel_Production")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal allocation found.")
            print(f"Minimum Total Fuel Expenses: {model.ObjVal:.2f} Klunz")

            print(
                "\nOptimal Allocation (Number of times each method is used):")
            print(f"  Furnace 1, Method 1 (x11): {x[0,0].X:.2f} times")
            print(f"  Furnace 1, Method 2 (x12): {x[0,1].X:.2f} times")
            print(f"  Furnace 2, Method 1 (x21): {x[1,0].X:.2f} times")
            print(f"  Furnace 2, Method 2 (x22): {x[1,1].X:.2f} times")

            # Verification of constraints
            print("\nVerification:")
            f1_hours = time_m1 * x[0, 0].X + time_m2 * x[0, 1].X
            f2_hours = time_m1 * x[1, 0].X + time_m2 * x[1, 1].X
            print(
                f"  Furnace 1 Hours Used: {f1_hours:.2f} / {max_furnace_hours}"
            )
            print(
                f"  Furnace 2 Hours Used: {f2_hours:.2f} / {max_furnace_hours}"
            )

            total_steel = steel_per_op * (x[0, 0].X + x[0, 1].X + x[1, 0].X +
                                          x[1, 1].X)
            print(
                f"  Total Steel Produced: {total_steel:.2f} tons (Min required: {min_total_steel})"
            )

        elif model.status == GRB.INFEASIBLE:
            print("Model is infeasible. Check constraints and parameters.")
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            # model.computeIIS()
            # model.write("steel_allocation_iis.ilp")
            # print("IIS written to steel_allocation_iis.ilp")
        else:
            print(f"Optimization stopped with status: {model.status}")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_steelmaking_allocation()
