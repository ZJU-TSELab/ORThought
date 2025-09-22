import gurobipy as gp
from gurobipy import GRB


def solve_complete_production_planning():
    """
    Solves the production planning problem with fixed activation costs,
    minimum batch sizes, and a shared time resource constraint.
    """
    try:
        # --- 1. Parameters ---
        products = ['A1', 'A2', 'A3']

        max_demand = {'A1': 5300, 'A2': 4500, 'A3': 5400}  # units of 100kg
        selling_price = {'A1': 124, 'A2': 109, 'A3': 115}  # $/100kg
        production_cost = {'A1': 73.30, 'A2': 52.90, 'A3': 65.40}  # $/100kg
        production_quota = {'A1': 500, 'A2': 450, 'A3': 550}  # 100kg units/day

        activation_cost = {'A1': 170000, 'A2': 150000, 'A3': 100000}  # $
        min_batch = {'A1': 20, 'A2': 20, 'A3': 16}  # units of 100kg

        available_days = 22

        # Pre-calculate profit per unit for clarity
        profit_per_unit = {
            p: selling_price[p] - production_cost[p]
            for p in products
        }

        # --- 2. Model Initialization ---
        model = gp.Model("CompleteProductionPlanning")

        # --- 3. Decision Variables ---
        # produce_qty[p]: quantity of product p to produce (in 100kg units)
        produce_qty = model.addVars(products,
                                    vtype=GRB.INTEGER,
                                    name="produce_qty",
                                    lb=0)

        # use_product[p]: binary variable, 1 if product p is produced, 0 otherwise
        use_product = model.addVars(products,
                                    vtype=GRB.BINARY,
                                    name="use_product")

        # --- 4. Objective Function ---
        # Maximize total profit = (sum of unit profits * quantity) - (sum of activation costs if produced)

        # Variable profit from units produced
        total_variable_profit = gp.quicksum(profit_per_unit[p] * produce_qty[p]
                                            for p in products)

        # Conditional activation costs
        total_activation_cost = gp.quicksum(activation_cost[p] * use_product[p]
                                            for p in products)

        model.setObjective(total_variable_profit - total_activation_cost,
                           GRB.MAXIMIZE)

        # --- 5. Constraints ---

        # Constraint 5.1: Shared Resource Constraint (Total Production Time)
        # The one that was missing from the "incorrect" code.
        model.addConstr(
            gp.quicksum(produce_qty[p] / production_quota[p] for p in products)
            <= available_days, "TotalProductionTime")

        # Constraints applied to each product individually
        for p in products:
            # Constraint 5.2: Maximum Demand Constraint
            # The production quantity cannot exceed market demand.
            model.addConstr(produce_qty[p] <= max_demand[p], f"MaxDemand_{p}")

            # Constraint 5.3: Link production quantity to the binary decision variable
            # If we decide to produce (use_product[p] = 1), then production quantity must be >= min_batch.
            # This correctly models the minimum batch size condition.
            model.addConstr(produce_qty[p] >= min_batch[p] * use_product[p],
                            f"MinBatchLink_{p}")

            # Constraint 5.4: Link the binary variable to an upper bound on production.
            # If we do not produce (use_product[p] = 0), quantity must be 0.
            # If we do produce (use_product[p] = 1), quantity is limited by a large number ("Big M").
            # A good "Big M" is the maximum possible demand for that product.
            model.addConstr(produce_qty[p] <= max_demand[p] * use_product[p],
                            f"ActivationLink_{p}")

        # --- 6. Optimize Model ---
        model.optimize()

        # --- 7. Results ---
        print("-" * 50)
        if model.status == GRB.OPTIMAL:
            print("Optimal production plan found!")
            print(f"Maximum Total Profit: ${model.objVal:,.2f}")
            print("-" * 50)
            print("Production Details:")
            total_days_used = 0
            for p in products:
                qty = produce_qty[p].X
                days_for_p = qty / production_quota[p]
                total_days_used += days_for_p

                print(f"  Product {p}:")
                if use_product[
                        p].X > 0.5:  # Check if this product was activated
                    print(f"    Status: PRODUCED")
                    print(f"    Produce Quantity (100kg units): {qty:.0f}")
                    print(f"    Days Used: {days_for_p:.2f} days")
                    net_profit_p = (profit_per_unit[p] *
                                    qty) - activation_cost[p]
                    print(
                        f"    Net Profit (incl. activation cost): ${net_profit_p:,.2f}"
                    )
                else:
                    print(f"    Status: NOT PRODUCED")
                print("-" * 25)

            print("Overall Resource Utilization:")
            print(
                f"  Total Production Days Used: {total_days_used:.2f} / {available_days} days"
            )
            print("-" * 50)

        elif model.status == GRB.INFEASIBLE:
            print(
                "Model is infeasible. No solution exists that satisfies all constraints."
            )
        else:
            print(f"Optimization was stopped with status: {model.status}")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    solve_complete_production_planning()
