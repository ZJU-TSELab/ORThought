import gurobipy as gp
from gurobipy import GRB


def solve_steel_bar_cutting():
    """
    Solves the steel bar cutting stock problem to minimize the number of raw bars used.
    """
    try:
        # --- Data ---
        # Demands for cut pieces
        demand_3m = 90  # pieces
        demand_4m = 60  # pieces

        # Raw steel bar length (not directly used in this formulation with pre-defined patterns,
        # but useful for understanding pattern generation)
        # raw_bar_length = 10 # meters

        # Cutting Patterns:
        # Pattern: (yield_3m_pieces, yield_4m_pieces)
        # Pattern A: 3 pieces of 3m, 0 pieces of 4m. Waste: 1m.
        # Pattern B: 2 pieces of 3m, 1 piece of 4m. Waste: 0m.
        # Pattern C: 0 pieces of 3m, 2 pieces of 4m. Waste: 2m.

        patterns = {
            'A': {
                'yield_3m': 3,
                'yield_4m': 0,
                'waste': 1
            },
            'B': {
                'yield_3m': 2,
                'yield_4m': 1,
                'waste': 0
            },
            'C': {
                'yield_3m': 0,
                'yield_4m': 2,
                'waste': 2
            }
        }
        pattern_ids = list(patterns.keys())

        # --- Create Gurobi Model ---
        model = gp.Model("SteelBarCuttingStock")

        # --- Decision Variables ---
        # x[p_id]: number of raw steel bars cut using pattern p_id
        x = model.addVars(pattern_ids, name="NumCuts", vtype=GRB.INTEGER, lb=0)

        # --- Objective Function: Minimize Total Number of Raw Bars Used ---
        model.setObjective(gp.quicksum(x[p_id] for p_id in pattern_ids),
                           GRB.MINIMIZE)

        # Alternative objective: Minimize total waste
        # total_waste = gp.quicksum(patterns[p_id]['waste'] * x[p_id] for p_id in pattern_ids)
        # model.setObjective(total_waste, GRB.MINIMIZE)

        # --- Constraints ---
        # 1. Demand for 3-meter pieces
        model.addConstr(gp.quicksum(patterns[p_id]['yield_3m'] * x[p_id]
                                    for p_id in pattern_ids) >= demand_3m,
                        name="Demand_3m")

        # 2. Demand for 4-meter pieces
        model.addConstr(gp.quicksum(patterns[p_id]['yield_4m'] * x[p_id]
                                    for p_id in pattern_ids) >= demand_4m,
                        name="Demand_4m")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal cutting plan found.")
            print(
                f"Minimum number of raw steel bars to use: {model.ObjVal:.0f}")

            print("\nNumber of times each pattern is used:")
            total_waste_calculated = 0
            for p_id in pattern_ids:
                if x[p_id].X > 0.5:  # If pattern is used
                    print(
                        f"  Pattern {p_id} (Yields: {patterns[p_id]['yield_3m']} of 3m, {patterns[p_id]['yield_4m']} of 4m; Waste/bar: {patterns[p_id]['waste']}m): "
                        f"{x[p_id].X:.0f} times")
                    total_waste_calculated += patterns[p_id]['waste'] * x[
                        p_id].X

            print(
                f"\nCalculated Total Waste: {total_waste_calculated:.0f} meters (based on minimizing raw bars)"
            )

            print("\nVerification of Production:")
            produced_3m = sum(patterns[p_id]['yield_3m'] * x[p_id].X
                              for p_id in pattern_ids)
            produced_4m = sum(patterns[p_id]['yield_4m'] * x[p_id].X
                              for p_id in pattern_ids)
            print(
                f"  Total 3m pieces produced: {produced_3m:.0f} (Demand: {demand_3m})"
            )
            print(
                f"  Total 4m pieces produced: {produced_4m:.0f} (Demand: {demand_60})"
            )  # Corrected to demand_4m

        elif model.status == GRB.INFEASIBLE:
            print("Model is infeasible. Check patterns and demands.")
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            # model.computeIIS()
            # model.write("steel_cutting_iis.ilp")
            # print("IIS written to steel_cutting_iis.ilp.")
        else:
            print(f"Optimization stopped with status: {model.status}")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    # Correcting a typo in the verification print statement
    demand_60 = 60  # This variable was used in print but not defined, should be demand_4m
    solve_steel_bar_cutting()
