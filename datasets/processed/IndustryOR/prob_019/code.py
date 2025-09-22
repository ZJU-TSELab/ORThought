import gurobipy as gp
from gurobipy import GRB


def solve_toy_production_problem():
    try:
        # --- Problem Data ---
        toys = ["robots", "cars", "blocks", "dolls"]
        profits = {"robots": 15, "cars": 8, "blocks": 12, "dolls": 5}

        # Resource consumption per toy
        plastic_usage = {"robots": 30, "cars": 10, "blocks": 20, "dolls": 15}
        electronics_usage = {"robots": 8, "cars": 5, "blocks": 3, "dolls": 2}

        # Resource availability
        max_plastic = 1200
        max_electronics = 800

        # --- Model Initialization ---
        model = gp.Model("BrightFutureToys")

        # --- Decision Variables ---
        # Quantity of each toy to produce (integer, non-negative)
        qty = model.addVars(toys, vtype=GRB.INTEGER, name="qty", lb=0)

        # Binary variables to indicate if a type of toy is manufactured
        # use_toy[t] = 1 if qty[t] > 0, 0 otherwise
        use_toy = model.addVars(toys, vtype=GRB.BINARY, name="use")

        # --- Objective Function ---
        # Maximize total profit
        total_profit = gp.quicksum(profits[t] * qty[t] for t in toys)
        model.setObjective(total_profit, GRB.MAXIMIZE)

        # --- Constraints ---

        # 1. Resource Constraints
        # Plastic
        model.addConstr(
            gp.quicksum(plastic_usage[t] * qty[t] for t in toys)
            <= max_plastic, "PlasticLimit")
        # Electronic Components
        model.addConstr(
            gp.quicksum(electronics_usage[t] * qty[t] for t in toys)
            <= max_electronics, "ElectronicsLimit")

        # 2. Link binary 'use_toy' variables to 'qty' variables
        # If qty[t] > 0, then use_toy[t] must be 1.
        # If qty[t] = 0, then use_toy[t] must be 0.
        # We can use a "big M" approach or indicator constraints. Indicators are cleaner.
        # A large enough M could be max_plastic / min_plastic_usage_per_toy or similar.
        # For example, max robots = 1200/30 = 40. max cars = 1200/10 = 120.
        # Let's use a simpler M for now, or better, indicator constraints.
        for t in toys:
            # (use_toy[t] == 1) => (qty[t] >= 1)
            model.addConstr((use_toy[t] == 1) >> (qty[t] >= 1),
                            f"Link_use_{t}_if_one")
            # (use_toy[t] == 0) => (qty[t] == 0)
            model.addConstr((use_toy[t] == 0) >> (qty[t] == 0),
                            f"Link_use_{t}_if_zero")

        # 3. Conditional Production Constraints
        # "If Bright Future Toys manufactures robots, they will not manufacture dolls."
        # This means if use_toy["robots"] = 1, then use_toy["dolls"] = 0 (which implies qty["dolls"] = 0).
        # A simple way to write this: use_toy["robots"] + use_toy["dolls"] <= 1
        model.addConstr(use_toy["robots"] + use_toy["dolls"] <= 1,
                        "Robots_No_Dolls")
        # Alternatively, using indicator:
        # model.addConstr((use_toy["robots"] == 1) >> (qty["dolls"] == 0), "Robots_No_Dolls_Indicator")

        # "However, if they manufacture model cars, they will also manufacture building blocks."
        # This means if use_toy["cars"] = 1, then use_toy["blocks"] = 1 (which implies qty["blocks"] >= 1).
        # use_toy["blocks"] >= use_toy["cars"]
        model.addConstr(use_toy["blocks"] >= use_toy["cars"],
                        "Cars_Implies_Blocks")
        # Alternatively, using indicator:
        # model.addConstr((use_toy["cars"] == 1) >> (qty["blocks"] >= 1), "Cars_Implies_Blocks_Indicator")

        # 4. Relationship Constraint
        # "The number of dolls manufactured cannot exceed the number of model cars manufactured."
        model.addConstr(qty["dolls"] <= qty["cars"], "Dolls_leq_Cars")

        # --- Optimize Model ---
        model.optimize()

        # --- Results ---
        print("-" * 40)
        if model.status == GRB.OPTIMAL:
            print("Optimal production plan found!")
            print(f"Maximum Total Profit: ${model.objVal:,.2f}")
            print("-" * 40)
            print("Production Quantities:")
            types_manufactured = 0
            for t in toys:
                qty_val = qty[t].X
                if qty_val > 0.5:  # Check if quantity is positive (accounting for potential float issues)
                    print(f"  {t.capitalize()}: {qty_val:.0f} units")
                    types_manufactured += 1
                else:
                    print(f"  {t.capitalize()}: 0 units")
            print("-" * 40)
            print(f"Total types of toys to manufacture: {types_manufactured}")
            print("-" * 40)

            print("Resource Utilization:")
            plastic_used = sum(plastic_usage[t] * qty[t].X for t in toys)
            electronics_used = sum(electronics_usage[t] * qty[t].X
                                   for t in toys)
            print(f"  Plastic Used: {plastic_used:.0f} / {max_plastic} units")
            print(
                f"  Electronic Components Used: {electronics_used:.0f} / {max_electronics} units"
            )
            print("-" * 40)

            print("Status of 'Use Toy' Variables (for verification):")
            for t in toys:
                print(
                    f"  Manufacture {t.capitalize()} (use_{t}): {use_toy[t].X:.0f}"
                )

        elif model.status == GRB.INFEASIBLE:
            print(
                "Model is infeasible. No solution exists that satisfies all constraints."
            )
            print(
                "Consider reviewing the constraints, especially the conditional ones and resource limits."
            )
        elif model.status == GRB.UNBOUNDED:
            print(
                "Model is unbounded. This typically means the objective can be improved indefinitely."
            )
        else:
            print(f"Optimization was stopped with status: {model.status}")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    solve_toy_production_problem()
