import gurobipy as gp
from gurobipy import GRB

def solve_ebike_battery_swapping(
    stations=["Van1", "Van2"],
    zones=["ZoneA", "ZoneB", "ZoneC"],
    dispatch_cost={"Van1": 300, "Van2": 320},
    van_capacity={"Van1": 150, "Van2": 180},
    op_cost_coeff={"Van1": 0.08, "Van2": 0.07},
    battery_demand={"ZoneA": 120, "ZoneB": 120, "ZoneC": 90}
):
    """
    Solves the E-Donkey Express battery swapping optimization problem.
    """
    # Create a new model
    model = gp.Model("EbikeBatterySwapping")

    # --- Decision Variables ---
    # Number of batteries replaced by station i in zone j
    batteries_replaced = model.addVars(stations,
                                       zones,
                                       vtype=GRB.INTEGER,
                                       name="BatteriesReplaced",
                                       lb=0)

    # Whether station i is used (dispatched)
    station_used = model.addVars(stations, vtype=GRB.BINARY, name="StationUsed")

    # --- Objective Function: Minimize Total Nightly Cost ---
    total_dispatch_cost = gp.quicksum(dispatch_cost[i] * station_used[i]
                                      for i in stations)

    # The operational cost is a quadratic term (cost = k * x^2)
    # Gurobi can handle quadratic objectives directly.
    total_operational_cost = gp.quicksum(
        op_cost_coeff[i] * batteries_replaced[i, j] * batteries_replaced[i, j]
        for i in stations for j in zones)

    model.setObjective(total_dispatch_cost + total_operational_cost,
                       GRB.MINIMIZE)

    # --- Constraints ---

    # 1. Demand Fulfillment constraint: All low-power batteries in each zone must be replaced.
    for j in zones:
        model.addConstr(
            gp.quicksum(batteries_replaced[i, j] for i in stations) ==
            battery_demand[j],
            name=f"DemandFulfillment_{j}")

    # 2. Van Capacity constraint: The number of batteries handled by a van cannot exceed its capacity.
    #    This constraint also links the station_used variable to the number of batteries replaced.
    #    If a van is not used (y_i=0), it cannot replace any batteries.
    for i in stations:
        model.addConstr(
            gp.quicksum(batteries_replaced[i, j] for j in zones) <=
            van_capacity[i] * station_used[i],
            name=f"Capacity_{i}")

    # Optimize the model
    # This is a Mixed-Integer Quadratically Constrained Program (MIQP).
    # The objective function is convex, so Gurobi will find the global optimum.
    model.optimize()

    # --- Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.objVal}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == '__main__':
    result = solve_ebike_battery_swapping()
    print(result)