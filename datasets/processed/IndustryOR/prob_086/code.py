import gurobipy as gp
from gurobipy import GRB


def solve_truck_rental():
    """
    Solves the truck rental optimization problem to minimize total cost
    while meeting refrigerated and non-refrigerated cargo requirements.
    """
    try:
        # --- Parameters ---
        truck_types = ['A', 'B']

        # Capacities (m^3 per truck)
        capacity_refrigerated = {'A': 20, 'B': 30}
        capacity_non_refrigerated = {'A': 40, 'B': 30}

        # Cargo Requirements (m^3)
        required_refrigerated = 3000
        required_non_refrigerated = 4000

        # Rental Costs (£ per truck - assumed for the task)
        rental_cost = {'A': 30, 'B': 40}

        # --- Create Gurobi Model ---
        model = gp.Model("TruckRentalOptimization")

        # --- Decision Variables ---
        # N[t]: Number of trucks of type t to rent
        N = model.addVars(truck_types,
                          name="NumTrucks",
                          vtype=GRB.INTEGER,
                          lb=0)

        # --- Objective Function: Minimize Total Rental Cost ---
        model.setObjective(
            gp.quicksum(rental_cost[t] * N[t] for t in truck_types),
            GRB.MINIMIZE)

        # --- Constraints ---
        # 1. Refrigerated Cargo Requirement
        model.addConstr(gp.quicksum(capacity_refrigerated[t] * N[t]
                                    for t in truck_types)
                        >= required_refrigerated,
                        name="RefrigeratedCapacity")

        # 2. Non-Refrigerated Cargo Requirement
        model.addConstr(gp.quicksum(capacity_non_refrigerated[t] * N[t]
                                    for t in truck_types)
                        >= required_non_refrigerated,
                        name="NonRefrigeratedCapacity")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal truck rental plan found.")
            print(f"Minimum Total Rental Cost: £{model.ObjVal:.2f}")

            print("\nNumber of Trucks to Rent:")
            for t in truck_types:
                print(f"  Type {t}: {N[t].X:.0f} trucks")

            print("\nCapacity Provided:")
            total_ref_cap = sum(capacity_refrigerated[t] * N[t].X
                                for t in truck_types)
            total_nonref_cap = sum(capacity_non_refrigerated[t] * N[t].X
                                   for t in truck_types)
            print(
                f"  Total Refrigerated Capacity: {total_ref_cap:.0f} m³ (Required: >= {required_refrigerated})"
            )
            print(
                f"  Total Non-Refrigerated Capacity: {total_nonref_cap:.0f} m³ (Required: >= {required_non_refrigerated})"
            )

        elif model.status == GRB.INFEASIBLE:
            print("Model is infeasible. Check constraints and requirements.")
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            # model.computeIIS()
            # model.write("truck_rental_iis.ilp")
            # print("IIS written to truck_rental_iis.ilp.")
        else:
            print(f"Optimization stopped with status: {model.status}")
            if model.SolCount == 0:
                print("No feasible solution found.")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_truck_rental()
