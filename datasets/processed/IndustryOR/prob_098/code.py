import gurobipy as gp
from gurobipy import GRB
import math  # For math.exp in results if needed


def solve_system_reliability():
    """
    Solves the system reliability optimization problem to determine the optimal
    number of spare parts for each component to maximize overall system reliability,
    subject to budget and weight constraints.
    Uses a log-transformed objective for Gurobi.
    """
    try:
        # --- Data ---
        num_components = 3
        components = range(
            num_components)  # Indices 0, 1, 2 for Components 1, 2, 3

        max_spares_per_component = 5
        num_spare_options = max_spares_per_component + 1
        spare_counts_options = range(num_spare_options)

        reliability_data = [
            [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],  # Component 1
            [0.6, 0.75, 0.95, 1.0, 1.0, 1.0],  # Component 2
            [0.7, 0.9, 1.0, 1.0, 1.0, 1.0]  # Component 3
        ]

        prices = [20, 30, 40]  # yuan
        weights = [2, 4, 6]  # kg

        max_budget = 150  # yuan
        max_weight = 20  # kg

        # --- Create Gurobi Model ---
        model = gp.Model("SystemReliabilityOptimization")

        # --- Decision Variables ---
        # x[c,s]: 1 if component c has s spares installed, 0 otherwise
        x = model.addVars(components,
                          spare_counts_options,
                          vtype=GRB.BINARY,
                          name="x_spares_selection")

        # Rel[c]: Achieved reliability of component c
        # Ensure Rel[c] is strictly positive for log function. Smallest reliability is 0.5.
        Rel = model.addVars(components,
                            name="Rel_component",
                            lb=0.0001,
                            ub=1.0,
                            vtype=GRB.CONTINUOUS)

        # log_Rel[c]: Natural logarithm of Rel[c]
        # Gurobi's log is natural log. The bounds for log_Rel depend on Rel's bounds.
        # log(0.0001) approx -9.21, log(1) = 0
        log_Rel = model.addVars(components,
                                name="log_Rel_component",
                                lb=-10,
                                ub=0.0,
                                vtype=GRB.CONTINUOUS)

        # --- Objective Function: Maximize Sum of Log(Reliabilities) ---
        # This is equivalent to maximizing the product of reliabilities.
        # Gurobi needs NonConvex=2 for general constraints like log.
        model.Params.NonConvex = 2
        model.setObjective(gp.quicksum(log_Rel[c] for c in components),
                           GRB.MAXIMIZE)

        # --- Constraints ---
        # 1. Unique Spare Count Selection: For each component c, exactly one x[c,s] is 1
        for c in components:
            model.addConstr(gp.quicksum(
                x[c, s_option] for s_option in spare_counts_options) == 1,
                            name=f"UniqueSpares_Comp{c+1}")

        # 2. Component Reliability Definition: Rel[c] = sum(Reliability_data[c][s_option] * x[c,s_option])
        for c in components:
            model.addConstr(Rel[c] == gp.quicksum(
                reliability_data[c][s_option] * x[c, s_option]
                for s_option in spare_counts_options),
                            name=f"DefineRel_Comp{c+1}")

        # 3. Link Rel[c] and log_Rel[c]: log_Rel[c] = log(Rel[c])
        for c in components:
            model.addGenConstrLog(Rel[c],
                                  log_Rel[c],
                                  name=f"LogConstraint_Comp{c+1}")

        # 4. Budget Constraint: sum_c sum_s (price[c] * s * x[c,s]) <= max_budget
        total_cost = gp.quicksum(prices[c] * s_option * x[c, s_option]
                                 for c in components
                                 for s_option in spare_counts_options)
        model.addConstr(total_cost <= max_budget, name="BudgetLimit")

        # 5. Weight Constraint: sum_c sum_s (weight[c] * s * x[c,s]) <= max_weight
        total_weight = gp.quicksum(weights[c] * s_option * x[c, s_option]
                                   for c in components
                                   for s_option in spare_counts_options)
        model.addConstr(total_weight <= max_weight, name="WeightLimit")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)
        model.setParam('MIPGap', 0.001)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal spare parts installation plan found.")
            # Calculate the actual system reliability (product of individual reliabilities)
            actual_system_reliability = 1.0
            for c in components:
                actual_system_reliability *= Rel[c].X

            print(
                f"Maximum System Operational Reliability: {actual_system_reliability:.4f} (or {actual_system_reliability*100:.2f}%)"
            )
            print(
                f"Objective Function Value (Sum of Log Reliabilities): {model.ObjVal:.4f}"
            )

            print("\nOptimal Number of Spare Parts for Each Component:")
            num_spares_chosen = {}
            for c in components:
                for s_option_val in spare_counts_options:
                    if x[c, s_option_val].X > 0.5:
                        num_spares_chosen[c] = s_option_val
                        print(
                            f"  Component {c+1}: Install {s_option_val} spare part(s)"
                        )
                        break

            print("\nAchieved Component Reliabilities:")
            for c in components:
                print(
                    f"  Component {c+1}: {Rel[c].X:.4f} (Reliability with {num_spares_chosen[c]} spares, log(Rel): {log_Rel[c].X:.4f})"
                )

            print("\nResource Usage:")
            final_cost = sum(prices[c] * num_spares_chosen[c]
                             for c in components)
            final_weight = sum(weights[c] * num_spares_chosen[c]
                               for c in components)
            print(
                f"  Total Cost: {final_cost:.2f} Yuan (Budget: <= {max_budget})"
            )
            print(
                f"  Total Weight: {final_weight:.2f} kg (Limit: <= {max_weight})"
            )

        elif model.status == GRB.INFEASIBLE:
            print(
                "Model is infeasible. The requirements cannot be met under the given budget and weight constraints."
            )
            model.computeIIS()
            model.write("system_reliability_iis.ilp")
            print("IIS written to system_reliability_iis.ilp for debugging.")
        elif model.status == GRB.INF_OR_UNBD:
            print("Model is infeasible or unbounded.")
        else:
            print(f"Optimization stopped with status: {model.status}")
            if model.SolCount == 0:
                print("No feasible solution found.")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
        print(f"Error message: {e.message}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_system_reliability()
