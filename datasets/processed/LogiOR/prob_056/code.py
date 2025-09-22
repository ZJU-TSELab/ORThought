import gurobipy as gp
from gurobipy import GRB


def solve_bus_scheduling(
    StartTime=0,
    EndTime=120,
    MinimumDepartureInterval=5,
    MaximumDepartureInterval=10,
    RoundtripTime=30,
    MaximumBuses=5
):
    """
    Solves the bus scheduling problem to minimize passenger waiting time.
    """
    # --- Sets ---
    TimeSlots = range(StartTime, EndTime + 1)

    # --- Model Initialization ---
    model = gp.Model("BusScheduling")

    # --- Decision Variables ---
    Departures = model.addVars(TimeSlots, vtype=GRB.BINARY, name="Departures")

    # --- Objective Function ---
    obj = gp.quicksum(
        (s - t)**2 * Departures[t] * Departures[s]
        for t in TimeSlots for s in TimeSlots if s > t
    )
    model.setObjective(obj, GRB.MINIMIZE)

    # --- Constraints ---
    # Min departure interval
    for t in TimeSlots:
        if t + MinimumDepartureInterval - 1 <= EndTime:
            model.addConstr(
                gp.quicksum(Departures[i] for i in range(t, t + MinimumDepartureInterval)) <= 1
            )

    # Max departure interval
    for t in TimeSlots:
        if t + MaximumDepartureInterval - 1 <= EndTime:
            model.addConstr(
                Departures[t] <= gp.quicksum(
                    Departures[s] for s in range(t + MinimumDepartureInterval, t + MaximumDepartureInterval)
                )
            )

    # Max number of departures
    max_departures = ((EndTime - StartTime) // RoundtripTime + 1) * MaximumBuses
    model.addConstr(gp.quicksum(Departures[t] for t in TimeSlots) <= max_departures)

    # Fixed departures at start and end
    model.addConstr(Departures[StartTime] == 1)
    model.addConstr(Departures[EndTime] == 1)

    # --- Optimize the model ---
    model.optimize()

    # --- Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_bus_scheduling()
    print(result)
