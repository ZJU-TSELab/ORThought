import gurobipy as gp
from gurobipy import GRB


def solve_healthy_pet_foods():
    """
    Solves the production planning problem for Healthy Pet Foods
    to maximize monthly profit.
    """
    try:
        # --- Parameters ---
        products = ['Meaties', 'Yummies']

        # Selling Price ($/pack)
        selling_price = {'Meaties': 2.80, 'Yummies': 2.00}

        # Raw Material Requirements (lbs/pack)
        grains_req = {'Meaties': 2.0, 'Yummies': 3.0}
        meat_req = {'Meaties': 3.0, 'Yummies': 1.5}

        # Variable Costs ($/pack) - Mixing and Packaging
        variable_cost = {'Meaties': 0.25, 'Yummies': 0.20}

        # Raw Material Costs ($/lb)
        cost_grains = 0.20
        cost_meat = 0.50

        # Resource Availability (per month)
        max_grains = 400000  # lbs
        max_meat = 300000  # lbs
        max_meaties_capacity = 90000  # packs

        # --- Calculate Profit per Pack ---
        # Profit = Selling Price - Grain Cost - Meat Cost - Variable Cost
        profit_per_pack = {}
        for p in products:
            cost_of_grains = grains_req[p] * cost_grains
            cost_of_meat = meat_req[p] * cost_meat
            profit_per_pack[p] = selling_price[
                p] - cost_of_grains - cost_of_meat - variable_cost[p]
            # print(f"Calculated profit for {p}: ${profit_per_pack[p]:.2f}") # For verification

        # --- Create Gurobi Model ---
        model = gp.Model("HealthyPetFoodsProfit")

        # --- Decision Variables ---
        # Produce[p]: Number of packs of product p produced per month
        Produce = model.addVars(products,
                                name="Produce",
                                vtype=GRB.CONTINUOUS,
                                lb=0)

        # --- Objective Function: Maximize Total Profit ---
        model.setObjective(
            gp.quicksum(profit_per_pack[p] * Produce[p] for p in products),
            GRB.MAXIMIZE)

        # --- Constraints ---
        # 1. Grain Availability Constraint
        model.addConstr(gp.quicksum(grains_req[p] * Produce[p]
                                    for p in products) <= max_grains,
                        name="GrainLimit")

        # 2. Meat Availability Constraint
        model.addConstr(gp.quicksum(meat_req[p] * Produce[p] for p in products)
                        <= max_meat,
                        name="MeatLimit")

        # 3. Meaties Production Capacity Constraint
        model.addConstr(Produce['Meaties'] <= max_meaties_capacity,
                        name="MeatiesCapacity")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal production plan found.")
            print(f"Maximum Monthly Profit: ${model.ObjVal:.2f}")

            print("\nOptimal Production Quantities (packs per month):")
            for p in products:
                print(f"  {p}: {Produce[p].X:.2f} packs")

            print("\nResource Utilization:")
            grains_used = sum(grains_req[p] * Produce[p].X for p in products)
            meat_used = sum(meat_req[p] * Produce[p].X for p in products)
            meaties_produced = Produce['Meaties'].X

            print(
                f"  Grains Used: {grains_used:.2f} / {max_grains} lbs "
                f"({(grains_used/max_grains*100) if max_grains > 0 else 0:.1f}%)"
            )
            print(f"  Meat Used: {meat_used:.2f} / {max_meat} lbs "
                  f"({(meat_used/max_meat*100) if max_meat > 0 else 0:.1f}%)")
            print(
                f"  Meaties Production: {meaties_produced:.2f} / {max_meaties_capacity} packs "
                f"({(meaties_produced/max_meaties_capacity*100) if max_meaties_capacity > 0 else 0:.1f}%)"
            )

        elif model.status == GRB.INFEASIBLE:
            print("Model is infeasible. Check constraints and data.")
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            # model.computeIIS()
            # model.write("healthy_pet_foods_iis.ilp")
            # print("IIS written to healthy_pet_foods_iis.ilp.")
        else:
            print(f"Optimization stopped with status: {model.status}")
            if model.SolCount == 0:
                print("No feasible solution found.")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_healthy_pet_foods()
