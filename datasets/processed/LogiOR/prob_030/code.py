import gurobipy as gp
from gurobipy import GRB


def solve_staffing_optimization(
    FixedCost=[1000, 2000],
    StaffCost=[500, 900],
    MaxStaffNum=[7, 7],
    ProcessRate=[[20, 25], [18, 22], [15, 20]],
    Demand=[120, 150, 200]):
    """
    Solves the distribution center staffing optimization problem.
    """
    # --- 1. Model Creation ---
    model = gp.Model("Distribution Center Staffing")

    # --- 2. Parameters & Sets ---
    Centers = range(len(FixedCost))
    GoodsTypes = range(len(Demand))

    # --- 3. Decision Variables ---
    # ActivatingCenter[c] = 1 if center c is activated, 0 otherwise
    ActivatingCenter = model.addVars(Centers,
                                     vtype=GRB.BINARY,
                                     name="ActivatingCenter")

    # StaffNum[c] = number of staff at center c
    StaffNum = model.addVars(Centers, vtype=GRB.INTEGER, name="StaffNum")

    # --- 4. Objective Function ---
    # Minimize total cost (fixed costs + staff costs)
    obj = gp.quicksum(FixedCost[c] * ActivatingCenter[c] +
                      StaffCost[c] * StaffNum[c] for c in Centers)
    model.setObjective(obj, GRB.MINIMIZE)

    # --- 5. Constraints ---
    # Constraint 1: Staff number constraint
    model.addConstrs(
        (StaffNum[c] <= MaxStaffNum[c] * ActivatingCenter[c] for c in Centers),
        name="StaffLimit")

    # Constraint 2: Demand satisfaction constraint
    model.addConstrs(
        (gp.quicksum(ProcessRate[g][c] * StaffNum[c] for c in Centers) >=
         Demand[g] for g in GoodsTypes),
        name="DemandSatisfaction")

    # --- 6. Solve the Model ---
    model.optimize()

    # --- 7. Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_staffing_optimization()
    print(result)