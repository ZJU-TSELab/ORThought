import gurobipy as gp
from gurobipy import GRB


def solve_vessel_berth_allocation(
    berth_length=900,
    best_berth_location=[375, 419, 591, 510, 567, 64, 507, 377, 93],
    expected_arrival_time=[9, 27, 34, 40, 1, 31, 28, 20, 22],
    operation_time=[7, 31, 31, 25, 29, 11, 28, 24, 20],
    vessel_length=[287, 196, 261, 288, 208, 238, 190, 217, 254],
    additional_travel_cost=[8, 4, 5, 5, 2, 6, 8, 6, 8],
    penalty_cost=[7, 7, 3, 4, 4, 7, 2, 4, 7],
    period=96,  # Note: This parameter is not used in the current model logic
    big_m=2000
):
    """
    Models and solves the Vessel Berth Allocation Problem (VBAP).
    """
    # --- 1. Model Creation ---
    model = gp.Model("VesselBerthAllocation")

    # --- 2. Sets ---
    # Derive the set of vessels from the length of the input data lists
    vessels = range(len(vessel_length))
    vessel_pairs = [(i, j) for i in vessels for j in vessels if i != j]

    # --- 3. Decision Variables ---
    # berth_location: position of each vessel along the quay
    berth_location = model.addVars(vessels, vtype=GRB.INTEGER, lb=0, name="berth_location")

    # berth_time: start time of berthing for each vessel
    berth_time = model.addVars(vessels, vtype=GRB.INTEGER, lb=0, name="berth_time")

    # location_relation[i,j]: 1 if vessel i is to the left of vessel j, 0 otherwise
    location_relation = model.addVars(vessel_pairs, vtype=GRB.BINARY, name="location_relation")

    # time_relation[i,j]: 1 if vessel i is berthed before vessel j, 0 otherwise
    time_relation = model.addVars(vessel_pairs, vtype=GRB.BINARY, name="time_relation")

    # position_deviation: auxiliary variable for absolute value of location deviation
    position_deviation = model.addVars(vessels, vtype=GRB.INTEGER, lb=0, name="position_deviation")

    # --- 4. Objective Function ---
    # Minimize total cost (travel deviation cost + delay penalty cost)
    objective = gp.quicksum(
        additional_travel_cost[i] * position_deviation[i] +
        penalty_cost[i] * (berth_time[i] - expected_arrival_time[i])
        for i in vessels
    )
    model.setObjective(objective, GRB.MINIMIZE)

    # --- 5. Constraints ---
    # Constraint 1: Linearize the absolute value for position deviation
    for i in vessels:
        model.addConstr(position_deviation[i] >= berth_location[i] - best_berth_location[i], name=f"abs_pos_dev_{i}")
        model.addConstr(position_deviation[i] >= best_berth_location[i] - berth_location[i], name=f"abs_neg_dev_{i}")

    # Constraint 2: Vessels must be fully within the berth's length
    for i in vessels:
        model.addConstr(berth_location[i] + vessel_length[i] <= berth_length, name=f"max_berth_loc_{i}")

    # Constraint 3: No spatial overlap between vessels (Big-M)
    for i, j in vessel_pairs:
        model.addConstr(
            berth_location[i] + vessel_length[i] <= berth_location[j] + big_m * (1 - location_relation[i, j]),
            name=f"loc_rel_{i}_{j}"
        )

    # Constraint 4: No temporal overlap between vessels (Big-M)
    for i, j in vessel_pairs:
        model.addConstr(
            berth_time[i] + operation_time[i] <= berth_time[j] + big_m * (1 - time_relation[i, j]),
            name=f"time_rel_{i}_{j}"
        )

    # Constraint 5: Vessels must not overlap in both space and time simultaneously.
    # For any pair of vessels (i, j), they must be separated either in space or in time.
    for i in vessels:
        for j in vessels:
            if i < j:
                model.addConstr(
                    location_relation[i, j] + location_relation[j, i] +
                    time_relation[i, j] + time_relation[j, i] >= 1,
                    name=f"no_overlap_{i}_{j}"
                )

    # Constraint 6: Vessels cannot be berthed before their expected arrival time
    for i in vessels:
        model.addConstr(berth_time[i] >= expected_arrival_time[i], name=f"arrival_time_{i}")

    # --- 6. Solve the Model ---
    model.setParam("OutputFlag", 0)  # Suppress Gurobi output
    model.optimize()

    # --- 7. Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == "__main__":
    result = solve_vessel_berth_allocation()
    print(result)
