import gurobipy as gp
from gurobipy import GRB


def solve_feed_mix_problem():
    """
    Solves the animal feed mix optimization problem using Gurobi.
    The goal is to minimize the cost of feed while meeting daily nutritional requirements.
    """
    try:
        # --- Data ---
        # Nutritional content per kg of feed: (Protein (g), Minerals (g), Vitamins (mg))
        # Price per kg of feed (¥/kg)

        feeds_data = {
            # Feed_ID: [Protein, Minerals, Vitamins, Price]
            1: [3, 1, 0.5, 0.2],
            2: [2, 0.5, 1, 0.7],
            3: [1, 0.2, 0.2, 0.4],
            4: [6, 2, 2, 0.3],
            5: [18, 0.5, 0.8, 0.8]
        }

        feed_ids = list(feeds_data.keys())

        # Daily nutritional requirements
        min_protein = 700  # g
        min_minerals = 30  # g
        min_vitamins = 100  # mg

        # --- Create a new model ---
        model = gp.Model("FeedMixOptimization")

        # --- Decision Variables ---
        # x[i]: amount of feed i to use, in kilograms (kg)
        x = model.addVars(feed_ids, name="x", lb=0.0, vtype=GRB.CONTINUOUS)

        # --- Objective Function ---
        # Minimize the total cost of the feed mixture
        # Cost = sum(price_i * x_i for i in feeds)
        total_cost = gp.quicksum(feeds_data[i][3] * x[i] for i in feed_ids)
        model.setObjective(total_cost, GRB.MINIMIZE)

        # --- Constraints ---
        # 1. Protein Requirement
        model.addConstr(
            gp.quicksum(feeds_data[i][0] * x[i] for i in feed_ids)
            >= min_protein, "ProteinRequirement")

        # 2. Minerals Requirement
        model.addConstr(
            gp.quicksum(feeds_data[i][1] * x[i] for i in feed_ids)
            >= min_minerals, "MineralsRequirement")

        # 3. Vitamins Requirement
        model.addConstr(
            gp.quicksum(feeds_data[i][2] * x[i] for i in feed_ids)
            >= min_vitamins, "VitaminsRequirement")

        # Suppress Gurobi output to console
        model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal feed mix found.")
            print(f"Minimum Cost: {model.objVal:.2f} ¥")
            print("\nAmount of each feed to use (kg):")
            total_feed_kg = 0
            for i in feed_ids:
                if x[i].X > 1e-6:  # Print only if the amount is significant
                    print(f"  Feed {i}: {x[i].X:.2f} kg")
                    total_feed_kg += x[i].X
            print(f"\nTotal kilograms of feed: {total_feed_kg:.2f} kg")

            # Verification of nutritional intake
            achieved_protein = sum(feeds_data[i][0] * x[i].X for i in feed_ids)
            achieved_minerals = sum(feeds_data[i][1] * x[i].X
                                    for i in feed_ids)
            achieved_vitamins = sum(feeds_data[i][2] * x[i].X
                                    for i in feed_ids)
            print("\nNutritional Intake with this mix:")
            print(
                f"  Protein: {achieved_protein:.2f} g (Required: >= {min_protein} g)"
            )
            print(
                f"  Minerals: {achieved_minerals:.2f} g (Required: >= {min_minerals} g)"
            )
            print(
                f"  Vitamins: {achieved_vitamins:.2f} mg (Required: >= {min_vitamins} mg)"
            )

        elif model.status == GRB.INFEASIBLE:
            print(
                "Model is infeasible. The nutritional requirements cannot be met with the given feeds under the specified constraints."
            )
            # You can compute and print IIS (Irreducible Inconsistent Subsystem) to help debug
            # model.computeIIS()
            # model.write("feed_mix_iis.ilp")
            # print("IIS written to feed_mix_iis.ilp. Review this file to find conflicting constraints.")
        else:
            print(f"Optimization was stopped with status: {model.status}")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_feed_mix_problem()
