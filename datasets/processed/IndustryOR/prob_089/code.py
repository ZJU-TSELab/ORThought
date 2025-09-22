import gurobipy as gp
from gurobipy import GRB


def solve_promotional_packages():
    """
    Solves the promotional package problem to maximize revenue,
    subject to inventory and minimum sales constraints.
    """
    try:
        # --- Parameters ---
        packages = ['A', 'B']

        # Inventory available
        avail_shirts = 200
        avail_pants = 100

        # Package composition (units per package)
        # composition[package][item]
        composition = {
            'A': {
                'shirts': 1,
                'pants': 2
            },
            'B': {
                'shirts': 3,
                'pants': 1
            }
        }

        # Package prices (£ per package)
        prices = {'A': 30, 'B': 50}

        # Minimum sales requirements (packages)
        min_sales = {'A': 20, 'B': 10}

        # --- Create Gurobi Model ---
        model = gp.Model("PromotionalPackages")

        # --- Decision Variables ---
        # N[p]: Number of packages of type p to sell
        N = model.addVars(packages,
                          name="NumPackages",
                          vtype=GRB.INTEGER,
                          lb=0)

        # --- Objective Function: Maximize Total Revenue ---
        model.setObjective(gp.quicksum(prices[p] * N[p] for p in packages),
                           GRB.MAXIMIZE)

        # --- Constraints ---
        # 1. Shirt Availability Constraint
        model.addConstr(gp.quicksum(composition[p]['shirts'] * N[p]
                                    for p in packages) <= avail_shirts,
                        name="ShirtLimit")

        # 2. Pants Availability Constraint
        model.addConstr(gp.quicksum(composition[p]['pants'] * N[p]
                                    for p in packages) <= avail_pants,
                        name="PantsLimit")

        # 3. Minimum Sales Requirements
        for p in packages:
            model.addConstr(N[p] >= min_sales[p], name=f"MinSales_{p}")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal package sales plan found.")
            print(f"Maximum Total Revenue: £{model.ObjVal:.2f}")

            print("\nNumber of Packages to Sell:")
            for p in packages:
                print(f"  Package {p}: {N[p].X:.0f} units")

            print("\nResource Utilization:")
            shirts_used = sum(composition[p]['shirts'] * N[p].X
                              for p in packages)
            pants_used = sum(composition[p]['pants'] * N[p].X
                             for p in packages)
            print(f"  Shirts Used: {shirts_used:.0f} / {avail_shirts}")
            print(f"  Pants Used: {pants_used:.0f} / {avail_pants}")

        elif model.status == GRB.INFEASIBLE:
            print(
                "Model is infeasible. Check constraints, inventory, and minimum sales requirements."
            )
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            # model.computeIIS()
            # model.write("promo_package_iis.ilp")
            # print("IIS written to promo_package_iis.ilp.")
        else:
            print(f"Optimization stopped with status: {model.status}")
            if model.SolCount == 0:
                print("No feasible solution found.")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_promotional_packages()
