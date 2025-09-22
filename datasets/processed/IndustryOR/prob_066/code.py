import gurobipy as gp
from gurobipy import GRB


def solve_production_inventory_planning():
    """
    Solves a multi-period production and inventory planning problem
    to minimize total production and inventory costs.
    """
    try:
        # --- Data ---
        products = ['ProdI', 'ProdII']
        # Months: July (0) to December (5)
        months = list(range(6))
        month_names = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # Demand (units/month) for ProdI, ProdII
        demand_data = {
            'ProdI': [30000, 30000, 30000, 100000, 100000, 100000],  # Jul-Dec
            'ProdII': [15000, 15000, 15000, 50000, 50000,
                       50000]  # Jul-Dec (Mar-Sep is 15k, other is 50k)
        }

        # Production cost (yuan/unit) for ProdI, ProdII
        # ProdI: Jan-May 5, Jun-Dec 4.5
        # ProdII: Jan-May 8, Jun-Dec 7
        production_cost_data = {
            'ProdI': [4.50] * 6,  # Jul-Dec
            'ProdII': [7.00] * 6  # Jul-Dec
        }

        max_combined_production_capacity = 120000  # units/month

        product_volume = {'ProdI': 0.2, 'ProdII': 0.4}  # m^3/unit

        factory_warehouse_capacity = 15000  # m^3
        factory_warehouse_cost = 1.0  # yuan/m^3/month
        external_warehouse_cost = 1.5  # yuan/m^3/month

        initial_inventory = {'ProdI': 0, 'ProdII': 0}  # units at start of July

        # --- Create Gurobi Model ---
        model = gp.Model("ProductionInventoryOptimization")

        # --- Decision Variables ---
        # Produce[p,t]: units of product p produced in month t
        produce_vars = model.addVars(products,
                                     months,
                                     name="Produce",
                                     lb=0.0,
                                     vtype=GRB.INTEGER)

        # InvFact[p,t]: units of product p in factory inventory at end of month t
        inv_fact_vars = model.addVars(products,
                                      months,
                                      name="InvFact",
                                      lb=0.0,
                                      vtype=GRB.INTEGER)

        # InvExt[p,t]: units of product p in external inventory at end of month t
        inv_ext_vars = model.addVars(products,
                                     months,
                                     name="InvExt",
                                     lb=0.0,
                                     vtype=GRB.INTEGER)

        # --- Objective Function: Minimize Total Costs ---
        total_production_cost = gp.quicksum(
            production_cost_data[p][t] * produce_vars[p, t] for p in products
            for t in months)

        total_factory_inv_cost = gp.quicksum(
            factory_warehouse_cost * product_volume[p] * inv_fact_vars[p, t]
            for p in products for t in months)

        total_external_inv_cost = gp.quicksum(
            external_warehouse_cost * product_volume[p] * inv_ext_vars[p, t]
            for p in products for t in months)

        model.setObjective(
            total_production_cost + total_factory_inv_cost +
            total_external_inv_cost, GRB.MINIMIZE)

        # --- Constraints ---
        for t in months:
            # 1. Combined Production Capacity Constraint
            model.addConstr(gp.quicksum(produce_vars[p, t] for p in products)
                            <= max_combined_production_capacity,
                            name=f"ProdCap_Month{t}")

            # 2. Factory Warehouse Capacity Constraint
            model.addConstr(gp.quicksum(product_volume[p] * inv_fact_vars[p, t]
                                        for p in products)
                            <= factory_warehouse_capacity,
                            name=f"FactWHCap_Month{t}")

            for p in products:
                # 3. Inventory Balance Constraint
                previous_total_inventory = initial_inventory[
                    p] if t == 0 else (inv_fact_vars[p, t - 1] +
                                       inv_ext_vars[p, t - 1])

                model.addConstr(
                    inv_fact_vars[p, t] +
                    inv_ext_vars[p, t] == previous_total_inventory +
                    produce_vars[p, t] - demand_data[p][t],
                    name=f"InvBalance_{p}_Month{t}")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal production and inventory plan found.")
            print(
                f"Minimum Total Cost (Production + Inventory): {model.ObjVal:.2f} Yuan"
            )

            print("\nMonthly Production Schedule (units):")
            print(f"{'Month':<5} | {'Product I':<12} | {'Product II':<12}")
            print("-" * 35)
            for t in months:
                print(
                    f"{month_names[t]:<5} | {produce_vars['ProdI',t].X:<12.2f} | {produce_vars['ProdII',t].X:<12.2f}"
                )

            print("\nEnd-of-Month Inventory Levels (units):")
            print(
                f"{'Month':<5} | {'ProdI Fact':<12} | {'ProdI Ext':<12} | {'ProdII Fact':<12} | {'ProdII Ext':<12} | {'Fact Vol':<10} | {'Ext Vol':<10}"
            )
            print("-" * 85)
            for t in months:
                vol_fact = product_volume['ProdI'] * inv_fact_vars[
                    'ProdI', t].X + product_volume['ProdII'] * inv_fact_vars[
                        'ProdII', t].X
                vol_ext = product_volume['ProdI'] * inv_ext_vars[
                    'ProdI', t].X + product_volume['ProdII'] * inv_ext_vars[
                        'ProdII', t].X
                print(
                    f"{month_names[t]:<5} | "
                    f"{inv_fact_vars['ProdI',t].X:<12.2f} | {inv_ext_vars['ProdI',t].X:<12.2f} | "
                    f"{inv_fact_vars['ProdII',t].X:<12.2f} | {inv_ext_vars['ProdII',t].X:<12.2f} | "
                    f"{vol_fact:<10.2f} | {vol_ext:<10.2f}")

            print(
                f"\nFactory Warehouse Capacity: {factory_warehouse_capacity} m^3"
            )

            total_prod_cost_val = sum(production_cost_data[p][t] *
                                      produce_vars[p, t].X for p in products
                                      for t in months)
            total_fact_inv_cost_val = sum(
                factory_warehouse_cost * product_volume[p] *
                inv_fact_vars[p, t].X for p in products for t in months)
            total_ext_inv_cost_val = sum(
                external_warehouse_cost * product_volume[p] *
                inv_ext_vars[p, t].X for p in products for t in months)
            print(f"\nCost Breakdown:")
            print(f"  Total Production Cost: {total_prod_cost_val:.2f} Yuan")
            print(
                f"  Total Factory Inventory Cost: {total_fact_inv_cost_val:.2f} Yuan"
            )
            print(
                f"  Total External Inventory Cost: {total_ext_inv_cost_val:.2f} Yuan"
            )

        elif model.status == GRB.INFEASIBLE:
            print(
                "Model is infeasible. Check constraints and data for contradictions."
            )
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            # model.computeIIS()
            # model.write("prod_inv_iis.ilp")
            # print("IIS written to prod_inv_iis.ilp.")
        else:
            print(f"Optimization stopped with status: {model.status}")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_production_inventory_planning()
