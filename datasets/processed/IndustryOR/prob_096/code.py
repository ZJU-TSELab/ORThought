import gurobipy as gp
from gurobipy import GRB


def solve_liquid_blending():
    """
    Solves the liquid blending problem to maximize profit, subject to
    raw material supply, product demand, and quality (sulfur) constraints.
    """
    try:
        # --- Data ---
        raw_materials = ['A', 'B', 'C', 'D']
        gasolines = ['GasA', 'GasB']

        # Sulfur content (%)
        sulfur_content = {'A': 0.03, 'B': 0.01, 'C': 0.02, 'D': 0.01}

        # Purchase prices (thousand yuan per ton)
        purchase_price = {'A': 6, 'B': 16, 'C': 10, 'D': 15}

        # Selling prices (thousand yuan per ton) - Same for both
        selling_price = {'GasA': 9.15, 'GasB': 9.15}

        # Max sulfur content allowed in products (%)
        max_sulfur = {'GasA': 0.025, 'GasB': 0.015}

        # Supply limits (tons) - Only D is limited
        supply_limit = {'D': 50}

        # Demand limits (tons)
        demand_limit = {'GasA': 100, 'GasB': 200}

        # --- Create Gurobi Model ---
        model = gp.Model("LiquidBlending")

        # --- Decision Variables ---
        # x[i, j]: amount (tons) of raw material i used in gasoline j
        x = model.addVars(raw_materials,
                          gasolines,
                          name="Blend",
                          lb=0.0,
                          vtype=GRB.CONTINUOUS)

        # --- Intermediate Expressions (Total Production) ---
        # Total amount of each gasoline produced
        GasProduced = {
            g: gp.quicksum(x[i, g] for i in raw_materials)
            for g in gasolines
        }

        # --- Objective Function: Maximize Total Profit ---
        # Profit = Total Revenue - Total Cost of Raw Materials
        total_revenue = gp.quicksum(selling_price[g] * GasProduced[g]
                                    for g in gasolines)

        total_cost = gp.quicksum(purchase_price[i] * x[i, g]
                                 for i in raw_materials for g in gasolines)

        model.setObjective(total_revenue - total_cost, GRB.MAXIMIZE)

        # --- Constraints ---
        # 1. Raw Material D Supply Limit
        model.addConstr(gp.quicksum(x['D', g] for g in gasolines)
                        <= supply_limit['D'],
                        name="SupplyLimit_D")

        # 2. Product Demand Limits
        for g in gasolines:
            model.addConstr(GasProduced[g] <= demand_limit[g],
                            name=f"DemandLimit_{g}")

        # 3. Sulfur Content Limits
        for g in gasolines:
            total_sulfur_in_g = gp.quicksum(sulfur_content[i] * x[i, g]
                                            for i in raw_materials)
            # total_sulfur_in_g <= max_sulfur[g] * GasProduced[g]
            model.addConstr(total_sulfur_in_g
                            <= max_sulfur[g] * GasProduced[g],
                            name=f"SulfurLimit_{g}")

            # Alternative formulation (avoids division by zero if GasProduced[g] could be 0):
            # (total_sulfur_in_g - max_sulfur[g] * GasProduced[g]) <= 0
            # model.addConstr(gp.quicksum((sulfur_content[i] - max_sulfur[g]) * x[i, g]
            #                             for i in raw_materials) <= 0,
            #                 name=f"SulfurLimit_{g}_alt")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal blending plan found.")
            # Convert profit back to yuan from thousand yuan
            print(f"Maximum Profit: {model.ObjVal * 1000:.2f} Yuan")

            print("\nOptimal Production Quantities (tons):")
            total_revenue_val = 0
            for g in gasolines:
                prod_qty = GasProduced[g].getValue()
                total_revenue_val += selling_price[g] * prod_qty
                print(f"  Gasoline {g}: {prod_qty:.2f} tons")
                if prod_qty > 1e-6:  # Avoid division by zero
                    print(f"    Composition:")
                    actual_sulfur_g = 0
                    for i in raw_materials:
                        if x[i, g].X > 1e-6:
                            percentage = (x[i, g].X / prod_qty * 100)
                            actual_sulfur_g += sulfur_content[i] * x[i, g].X
                            print(
                                f"      Raw Material {i}: {x[i,g].X:.2f} tons ({percentage:.1f}%)"
                            )
                    actual_sulfur_percent = (actual_sulfur_g / prod_qty *
                                             100) if prod_qty > 1e-6 else 0
                    print(
                        f"    -> Actual Sulfur Content: {actual_sulfur_percent:.3f}% (Max: {max_sulfur[g]*100:.1f}%)"
                    )

            print("\nRaw Material Usage (tons):")
            total_cost_val = 0
            for i in raw_materials:
                usage = sum(x[i, g].X for g in gasolines)
                cost_i = purchase_price[i] * usage
                total_cost_val += cost_i
                limit_str = f"(Limit: {supply_limit[i]})" if i in supply_limit else ""
                print(f"  Raw Material {i}: {usage:.2f} tons {limit_str}")

            print("\nFinancial Summary (Thousand Yuan):")
            print(f"  Total Revenue: {total_revenue_val:.3f}")
            print(f"  Total Raw Material Cost: {total_cost_val:.3f}")
            print(
                f"  Calculated Profit: {(total_revenue_val - total_cost_val):.3f}"
            )

        elif model.status == GRB.INFEASIBLE:
            print(
                "Model is infeasible. Check constraints, demands, supply, and quality requirements."
            )
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            # model.computeIIS()
            # model.write("liquid_blending_iis.ilp")
            # print("IIS written to liquid_blending_iis.ilp for debugging.")
        else:
            print(f"Optimization stopped with status: {model.status}")
            if model.SolCount == 0:
                print("No feasible solution found.")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_liquid_blending()
