import gurobipy as gp
from gurobipy import GRB


def solve_fertilizer_production():
    """
    Solves the fertilizer production planning problem to maximize
    the total ending inventory for the week.
    """
    try:
        # --- Parameters ---
        products = ['Liquid', 'Solid']
        machines = [1, 2]

        # Time requirements (minutes/unit)
        # time_req[product][machine]
        time_req = {'Liquid': {1: 50, 2: 30}, 'Solid': {1: 24, 2: 33}}

        # Available machine time (minutes/week)
        avail_machine_time = {
            1: 40 * 60,  # 2400 minutes
            2: 35 * 60  # 2100 minutes
        }

        # Initial inventory (units)
        initial_inventory = {'Liquid': 30, 'Solid': 90}

        # Demand (units/week)
        demand = {'Liquid': 75, 'Solid': 95}

        # --- Create Gurobi Model ---
        model = gp.Model("FertilizerProduction")

        # --- Decision Variables ---
        # Produce[p]: Number of units of product p produced this week
        Produce = model.addVars(products,
                                name="Produce",
                                vtype=GRB.INTEGER,
                                lb=0)

        # InvEnd[p]: Inventory of product p at the end of the week
        # We must ensure it's non-negative, which implicitly forces demand to be met.
        InvEnd = model.addVars(products,
                               name="InvEnd",
                               vtype=GRB.INTEGER,
                               lb=0)

        # --- Objective Function: Maximize Total Ending Inventory ---
        model.setObjective(gp.quicksum(InvEnd[p] for p in products),
                           GRB.MAXIMIZE)

        # --- Constraints ---
        # 1. Machine Time Constraints
        for m in machines:
            model.addConstr(gp.quicksum(time_req[p][m] * Produce[p]
                                        for p in products)
                            <= avail_machine_time[m],
                            name=f"Machine{m}_TimeLimit")

        # 2. Inventory Balance Constraints
        # Ending Inventory = Initial Inventory + Production - Demand
        for p in products:
            model.addConstr(InvEnd[p] == initial_inventory[p] + Produce[p] -
                            demand[p],
                            name=f"InventoryBalance_{p}")

        # Note: The constraint InvEnd[p] >= 0 implicitly handles the demand requirement.
        # If demand cannot be met, the problem will be infeasible.

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal production plan found.")
            print(f"Maximum Total Ending Inventory: {model.ObjVal:.0f} units")

            print("\nProduction Quantities (units per week):")
            for p in products:
                print(f"  Product {p}: {Produce[p].X:.0f} units")

            print("\nEnding Inventory (units):")
            for p in products:
                print(f"  Product {p}: {InvEnd[p].X:.0f} units")

            print("\nResource Utilization:")
            for m in machines:
                time_used = sum(time_req[p][m] * Produce[p].X
                                for p in products)
                print(
                    f"  Machine {m} Time Used: {time_used:.2f} / {avail_machine_time[m]} minutes "
                    f"({(time_used/avail_machine_time[m]*100) if avail_machine_time[m] > 0 else 0:.1f}%)"
                )

            print("\nDemand Fulfillment Check:")
            for p in products:
                available = initial_inventory[p] + Produce[p].X
                print(
                    f"  Product {p}: Available={available:.0f}, Demand={demand[p]}"
                )

        elif model.status == GRB.INFEASIBLE:
            print(
                "Model is infeasible. Check constraints, demand, and available time."
            )
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            # model.computeIIS()
            # model.write("fertilizer_production_iis.ilp")
            # print("IIS written to fertilizer_production_iis.ilp.")
        else:
            print(f"Optimization stopped with status: {model.status}")
            if model.SolCount == 0:
                print("No feasible solution found.")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_fertilizer_production()
