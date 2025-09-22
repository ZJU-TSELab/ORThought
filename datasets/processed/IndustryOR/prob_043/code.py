import gurobipy as gp
from gurobipy import GRB


def solve_fixed_charge_transshipment():
    """
    Solves a fixed-charge transshipment problem with intermediate marshaling stations.
    The goal is to minimize total transportation and fixed operational costs.
    """
    try:
        # --- Data ---
        # Production points (sources)
        production_points = [1, 2]
        supply = {1: 100, 2: 150}  # a_i

        # Demand points (sinks)
        demand_points = [1, 2]
        demand = {1: 80, 2: 120}  # b_j

        # Marshaling stations
        marshaling_stations = [1, 2]
        fixed_costs = {1: 10, 2: 15}  # f_k
        station_capacities = {1: 100, 2: 100}  # q_k

        # Unit transportation costs from production i to station k (c_ik)
        cost_ik = {(1, 1): 2, (1, 2): 3, (2, 1): 4, (2, 2): 1}

        # Unit transportation costs from station k to demand j (c'_kj)
        cost_kj = {(1, 1): 3, (1, 2): 2, (2, 1): 1, (2, 2): 4}

        # --- Create Gurobi Model ---
        model = gp.Model("FixedChargeTransshipment")

        # --- Decision Variables ---
        # x[i,k]: amount shipped from production point i to marshaling station k
        x = model.addVars(production_points,
                          marshaling_stations,
                          name="x",
                          lb=0.0,
                          vtype=GRB.CONTINUOUS)

        # y[k,j]: amount shipped from marshaling station k to demand point j
        y = model.addVars(marshaling_stations,
                          demand_points,
                          name="y",
                          lb=0.0,
                          vtype=GRB.CONTINUOUS)

        # u[k]: 1 if marshaling station k is used, 0 otherwise
        u = model.addVars(marshaling_stations, name="u", vtype=GRB.BINARY)

        # --- Objective Function: Minimize Total Cost ---
        var_cost_ik = gp.quicksum(cost_ik[i, k] * x[i, k]
                                  for i in production_points
                                  for k in marshaling_stations)
        var_cost_kj = gp.quicksum(cost_kj[k, j] * y[k, j]
                                  for k in marshaling_stations
                                  for j in demand_points)
        total_fixed_cost = gp.quicksum(fixed_costs[k] * u[k]
                                       for k in marshaling_stations)

        model.setObjective(var_cost_ik + var_cost_kj + total_fixed_cost,
                           GRB.MINIMIZE)

        # --- Constraints ---
        # 1. Supply Constraints: sum_k x[i,k] <= supply[i] for each i
        for i in production_points:
            model.addConstr(gp.quicksum(x[i, k] for k in marshaling_stations)
                            <= supply[i],
                            name=f"Supply_{i}")

        # 2. Demand Constraints: sum_k y[k,j] == demand[j] for each j
        for j in demand_points:
            model.addConstr(gp.quicksum(
                y[k, j] for k in marshaling_stations) == demand[j],
                            name=f"Demand_{j}")

        # 3. Flow Conservation at Marshaling Stations: sum_i x[i,k] == sum_j y[k,j] for each k
        for k in marshaling_stations:
            model.addConstr(gp.quicksum(
                x[i, k] for i in production_points) == gp.quicksum(
                    y[k, j] for j in demand_points),
                            name=f"FlowCons_Station_{k}")

        # 4. Marshaling Station Capacity and Usage: sum_i x[i,k] <= capacity[k] * u[k] for each k
        for k in marshaling_stations:
            model.addConstr(gp.quicksum(x[i, k] for i in production_points)
                            <= station_capacities[k] * u[k],
                            name=f"Capacity_Station_{k}")

        # Suppress Gurobi output to console if desired
        # model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()

        # --- Results ---
        if model.status == GRB.OPTIMAL:
            print("Optimal transportation plan found.")
            print(f"Minimum Total Cost: {model.ObjVal:.2f}")

            print(
                "\nShipments from Production Points to Marshaling Stations (x_ik):"
            )
            for i in production_points:
                for k in marshaling_stations:
                    if x[i, k].X > 1e-6:  # Print only if flow is significant
                        print(
                            f"  From Production {i} to Station {k}: {x[i,k].X:.2f} units"
                        )

            print(
                "\nShipments from Marshaling Stations to Demand Points (y_kj):"
            )
            for k in marshaling_stations:
                for j in demand_points:
                    if y[k, j].X > 1e-6:  # Print only if flow is significant
                        print(
                            f"  From Station {k} to Demand {j}: {y[k,j].X:.2f} units"
                        )

            print("\nMarshaling Station Usage (u_k):")
            total_flow_through_station = {}
            for k in marshaling_stations:
                flow = sum(x[i, k].X for i in production_points)
                total_flow_through_station[k] = flow
                if u[k].X > 0.5:  # If station is used
                    print(
                        f"  Station {k}: Used (Fixed Cost: {fixed_costs[k]}). Flow: {flow:.2f} / Capacity: {station_capacities[k]}"
                    )
                else:
                    print(f"  Station {k}: Not Used. Flow: {flow:.2f}")

            # Verification
            print("\nVerification:")
            print("  Supply Check:")
            for i in production_points:
                shipped_from_i = sum(x[i, k].X for k in marshaling_stations)
                print(
                    f"    Production {i}: Shipped {shipped_from_i:.2f}, Supply {supply[i]}"
                )

            print("  Demand Check:")
            for j in demand_points:
                received_at_j = sum(y[k, j].X for k in marshaling_stations)
                print(
                    f"    Demand {j}: Received {received_at_j:.2f}, Demand {demand[j]}"
                )

            print("  Station Flow Conservation Check:")
            for k in marshaling_stations:
                inflow_k = sum(x[i, k].X for i in production_points)
                outflow_k = sum(y[k, j].X for j in demand_points)
                print(
                    f"    Station {k}: Inflow={inflow_k:.2f}, Outflow={outflow_k:.2f} (Difference: {inflow_k - outflow_k:.2f})"
                )

        elif model.status == GRB.INFEASIBLE:
            print("Model is infeasible. Check constraints and parameters.")
            # Compute and print IIS (Irreducible Inconsistent Subsystem)
            # model.computeIIS()
            # model.write("transshipment_iis.ilp")
            # print("IIS written to transshipment_iis.ilp.")
        else:
            print(f"Optimization stopped with status: {model.status}")

    except gp.GurobiError as e:
        print(f"Gurobi error code {e.errno}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    solve_fixed_charge_transshipment()
