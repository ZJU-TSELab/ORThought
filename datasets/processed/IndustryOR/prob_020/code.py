import gurobipy as gp
from gurobipy import GRB


def solve_restaurant_table_order_problem():
    try:
        # --- Problem Data ---
        # Costs per table
        cost_per_table_A = 120
        cost_per_table_B = 110
        cost_per_table_C = 100

        # Tables per order
        tables_per_order_A = 20
        tables_per_order_B = 15
        tables_per_order_C = 15

        # Cost per order (derived)
        cost_per_order_A = cost_per_table_A * tables_per_order_A
        cost_per_order_B = cost_per_table_B * tables_per_order_B
        cost_per_order_C = cost_per_table_C * tables_per_order_C

        # Total table quantity limits
        min_total_tables = 150
        max_total_tables = 600

        # Conditional requirement: if A is used, at least 30 tables from B
        min_tables_from_B_if_A = 30
        # Calculate minimum orders from B if A is used
        min_orders_from_B_if_A = -(
            -min_tables_from_B_if_A // tables_per_order_B)  # Ceiling division

        # --- Model Creation ---
        model = gp.Model("RestaurantTableOrderOptimization")

        # --- Decision Variables ---
        # Number of orders from each supplier (must be integer, non-negative)
        orders_A = model.addVar(vtype=GRB.INTEGER, name="Orders_A", lb=0)
        orders_B = model.addVar(vtype=GRB.INTEGER, name="Orders_B", lb=0)
        orders_C = model.addVar(vtype=GRB.INTEGER, name="Orders_C", lb=0)

        # Binary variables to indicate if any order is placed with a supplier
        # use_A = 1 if orders_A > 0, 0 otherwise
        # use_B = 1 if orders_B > 0, 0 otherwise
        use_A = model.addVar(vtype=GRB.BINARY, name="Use_A")
        use_B = model.addVar(vtype=GRB.BINARY, name="Use_B")
        # use_C is not strictly needed for the B->C condition if directly linking orders_C to use_B,
        # but can be added for clarity if desired. For now, we'll derive its usage.

        # --- Objective Function ---
        # Minimize the total cost of ordering
        total_cost = (orders_A * cost_per_order_A +
                      orders_B * cost_per_order_B +
                      orders_C * cost_per_order_C)
        model.setObjective(total_cost, GRB.MINIMIZE)

        # --- Constraints ---

        # 1. Calculate total number of tables ordered
        total_tables_ordered = (orders_A * tables_per_order_A +
                                orders_B * tables_per_order_B +
                                orders_C * tables_per_order_C)

        # 2. Total tables constraints
        model.addConstr(total_tables_ordered >= min_total_tables,
                        "MinTotalTables")
        model.addConstr(total_tables_ordered <= max_total_tables,
                        "MaxTotalTables")

        # 3. Link binary 'use' variables to the number of orders
        # Gurobi's indicator constraints are suitable here.
        # (use_A == 1) => (orders_A >= 1)
        # (use_A == 0) => (orders_A == 0)
        model.addConstr((use_A == 1) >> (orders_A >= 1), "Link_use_A_if_one")
        model.addConstr((use_A == 0) >> (orders_A == 0), "Link_use_A_if_zero")

        # Similarly for use_B and orders_B
        model.addConstr((use_B == 1) >> (orders_B >= 1), "Link_use_B_if_one")
        model.addConstr((use_B == 0) >> (orders_B == 0), "Link_use_B_if_zero")

        # 4. Conditional ordering constraints:
        # "If the restaurant decides to order tables from Supplier A (use_A = 1),
        # it must also order at least 30 tables from Supplier B."
        # This means orders_B * tables_per_order_B >= 30, so orders_B >= min_orders_from_B_if_A.
        model.addConstr((use_A == 1) >> (orders_B >= min_orders_from_B_if_A),
                        "Conditional_A_implies_B_orders")

        # "Additionally, if the restaurant decides to order tables from Supplier B (use_B = 1),
        # it must also order tables from Supplier C (orders_C >= 1)."
        model.addConstr((use_B == 1) >> (orders_C >= 1),
                        "Conditional_B_implies_C_orders")

        # --- Optimize Model ---
        model.optimize()

        # --- Results ---
        print("-" * 40)
        if model.status == GRB.OPTIMAL:
            print("Optimal solution found!")
            print(f"Minimum Total Cost: ${model.objVal:,.2f}")
            print("-" * 40)
            print("Order Plan:")
            print(f"  Orders from Supplier A: {orders_A.X:.0f}")
            print(f"    Tables from A: {orders_A.X * tables_per_order_A:.0f}")
            print(f"  Orders from Supplier B: {orders_B.X:.0f}")
            print(f"    Tables from B: {orders_B.X * tables_per_order_B:.0f}")
            print(f"  Orders from Supplier C: {orders_C.X:.0f}")
            print(f"    Tables from C: {orders_C.X * tables_per_order_C:.0f}")
            print("-" * 40)

            actual_total_tables = (orders_A.X * tables_per_order_A +
                                   orders_B.X * tables_per_order_B +
                                   orders_C.X * tables_per_order_C)
            print(f"Total Tables Ordered: {actual_total_tables:.0f}")
            print(
                f"  (Min required: {min_total_tables}, Max allowed: {max_total_tables})"
            )
            print("-" * 40)

            print("Status of 'Use Supplier' Variables (for verification):")
            print(f"  Use Supplier A (use_A): {use_A.X:.0f}")
            print(f"  Use Supplier B (use_B): {use_B.X:.0f}")
            if orders_C.X > 0.5:  # Check if C was used
                print(f"  Use Supplier C: 1 (derived from orders_C > 0)")
            else:
                print(f"  Use Supplier C: 0 (derived from orders_C == 0)")

        elif model.status == GRB.INFEASIBLE:
            print(
                "Model is infeasible. No solution exists that satisfies all constraints."
            )
            print(
                "Consider reviewing the constraints, especially the conditional ones and table limits."
            )
            # You can compute and print an Irreducible Inconsistent Subsystem (IIS)
            # to help debug infeasibility:
            # model.computeIIS()
            # model.write("model_iis.ilp")
            # print("IIS written to model_iis.ilp")
        elif model.status == GRB.UNBOUNDED:
            print(
                "Model is unbounded. This typically means the objective can be improved indefinitely,"
            )
            print(
                "which might indicate an issue with constraints or objective direction for minimization."
            )
        else:
            print(f"Optimization was stopped with status: {model.status}")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    solve_restaurant_table_order_problem()
