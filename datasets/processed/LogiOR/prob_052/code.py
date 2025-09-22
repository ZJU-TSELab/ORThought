import gurobipy as gp
from gurobipy import GRB


def solve_facility_location(
    facilities=['F1', 'F2', 'F3', 'F4', 'F5'],
    residentials=['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8'],
    travel_time={
        'F1': [8, 12, 9, 15, 7, 11, 14, 6],
        'F2': [10, 8, 13, 7, 9, 12, 5, 11],
        'F3': [14, 6, 10, 8, 12, 7, 9, 13],
        'F4': [7, 11, 14, 6, 8, 10, 12, 9],
        'F5': [9, 13, 7, 11, 6, 14, 8, 10]
    }
):
    """
    Solves the facility location problem.
    """
    # Create coverage parameter a_fr (1 if travel time <=10, 0 otherwise)
    coverage = {}
    for f in facilities:
        for i, r in enumerate(residentials):
            coverage[(f, r)] = 1 if travel_time[f][i] <= 10 else 0

    # Create model
    model = gp.Model("Facility_Location")

    # Decision variables: x_f (whether facility f is selected)
    x = model.addVars(facilities, vtype=GRB.BINARY, name="Select")

    # Objective: minimize number of selected facilities
    model.setObjective(gp.quicksum(x[f] for f in facilities), GRB.MINIMIZE)

    # Constraints: each residential area must be covered by at least one selected facility
    for r in residentials:
        model.addConstr(gp.quicksum(coverage[(f, r)] * x[f] for f in facilities) >= 1,
                        f"Cover_{r}")

    # Solve the model
    model.optimize()

    # Return results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_facility_location()
    print(result)