import gurobipy as gp
from gurobipy import GRB


def solve_truck_assignment(
    trucks=[1, 2, 3, 4],
    locations=[1, 2, 3, 4],
    cost={
        (1, 1): 120, (1, 2): 150, (1, 3): 180, (1, 4): 90,
        (2, 1): 110, (2, 2): 140, (2, 3): 170, (2, 4): 80,
        (3, 1): 130, (3, 2): 160, (3, 3): 190, (3, 4): 100,
        (4, 1): 140, (4, 2): 170, (4, 3): 200, (4, 4): 110
    }
):
    """
    Solves the truck assignment problem.
    """
    # Create optimization model
    model = gp.Model("TruckAssignment")

    # Decision variables: x[t,l] = 1 if truck t is assigned to location l
    x = model.addVars(trucks, locations, vtype=GRB.BINARY, name="assign")

    # Set objective: minimize total transportation cost
    model.setObjective(gp.quicksum(cost[t, l] * x[t, l] for t in trucks for l in locations), GRB.MINIMIZE)

    # Constraints:
    # Each truck must be assigned to exactly one location
    model.addConstrs((x.sum(t, '*') == 1 for t in trucks), name="truck_assignment")

    # Each location must receive exactly one truck
    model.addConstrs((x.sum('*', l) == 1 for l in locations), name="location_assignment")

    # Optimize the model
    model.optimize()

    # Return results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_truck_assignment()
    print(result)