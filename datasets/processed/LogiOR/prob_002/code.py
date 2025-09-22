import gurobipy as gp
from gurobipy import GRB


def solve_flight_gate_assignment(
    gates=[1, 2],
    flights=[1, 2, 3, 4],
    arrange_start_time={1: 600, 2: 630, 4: 645, 3: 675},
    duration={1: 60, 2: 60, 3: 75, 4: 60},
    cost_per_delay=1,
    big_m=1500,
):
    """
    Models and solves the flight gate assignment problem to minimize total delay.
    """
    # --- 1. Model Creation ---
    model = gp.Model("FlightGateAssignment")

    # --- 2. Decision Variables ---
    # x[f,g] = 1 if flight f is assigned to gate g, else 0
    x = model.addVars([(f, g) for f in flights for g in gates], vtype=GRB.BINARY, name="x")

    # s[f] = actual start time of flight f
    s = model.addVars(flights, vtype=GRB.INTEGER, name="s")

    # --- 3. Objective Function ---
    # Minimize total delay cost
    obj = gp.quicksum(cost_per_delay * (s[f] - arrange_start_time[f])
                      for f in flights)
    model.setObjective(obj, GRB.MINIMIZE)

    # --- 4. Constraints ---
    # Constraint 1: Actual start time should be greater than or equal to the scheduled start time
    for f in flights:
        model.addConstr(s[f] >= arrange_start_time[f], f"start_time_constraint_{f}")

    # Constraint 2: Every flight should be assigned to exactly one gate
    for f in flights:
        model.addConstr(gp.quicksum(x[f, g] for g in gates) == 1, f"one_gate_per_flight_{f}")

    # Constraint 3: The actual start time should be greater than or equal to the end time
    # of the previous flight at the same gate (linearized using Big-M).
    # This formulation imposes a fixed sequence f1 -> f2 if f1 < f2.
    for g in gates:
        for f1 in flights:
            for f2 in flights:
                if f1 < f2:  # for flights where f1 comes before f2
                    # If both flights are assigned to the same gate g,
                    # then f2 must start after f1 ends
                    model.addConstr(
                        s[f2] >= s[f1] + duration[f1] - big_m * (2 - x[f1, g] - x[f2, g]),
                        f"sequence_constraint_{f1}_{f2}_{g}",
                    )

    # --- 5. Solve the Model ---
    # model.setParam("OutputFlag", 0) # Suppress Gurobi output
    model.optimize()

    # --- 6. Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == "__main__":
    result = solve_flight_gate_assignment()
    print(result)