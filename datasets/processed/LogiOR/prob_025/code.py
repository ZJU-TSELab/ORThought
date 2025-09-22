import gurobipy as gp
from gurobipy import GRB


def solve_production_planning(
    RegularTimeProductionLimit=6000,
    OvertimeProductionLimit=2000,
    RegularTimeCost=2,
    OvertimeCost=3,
    InventoryHoldingCost=0.5,
    Demand=[5000, 6000, 5500, 7000, 4500, 4000]):
    """
    Solves the production planning optimization problem.
    """
    # Create a new model
    model = gp.Model("Production Planning")

    # Parameters
    MonthNum = len(Demand)

    # Define month set (1-indexed to match the model description)
    Months = range(1, MonthNum + 1)

    # Decision Variables
    RegularTimeProduction = model.addVars(Months,
                                          vtype=GRB.INTEGER,
                                          name="RegularTimeProduction")
    OvertimeProduction = model.addVars(Months,
                                       vtype=GRB.INTEGER,
                                       name="OvertimeProduction")
    Inventory = model.addVars(Months, vtype=GRB.INTEGER, name="Inventory")

    # Objective: Minimize total cost
    objective = gp.quicksum(RegularTimeCost * RegularTimeProduction[m] +
                            OvertimeCost * OvertimeProduction[m] +
                            InventoryHoldingCost * Inventory[m] for m in Months)
    model.setObjective(objective, GRB.MINIMIZE)

    # Constraint 1: Initial inventory constraint
    model.addConstr(
        Inventory[1] == RegularTimeProduction[1] + OvertimeProduction[1] -
        Demand[0], "InitialInventory")

    # Constraint 2: Inventory balance constraint for months after the first
    model.addConstrs(
        (Inventory[m] == Inventory[m - 1] + RegularTimeProduction[m] +
         OvertimeProduction[m] - Demand[m - 1]
         for m in range(2, MonthNum + 1)), "InventoryBalance")

    # Constraint 3: Demand constraint
    # Note: This is redundant given inventory balance and non-negative inventory
    model.addConstrs(
        (RegularTimeProduction[m] + OvertimeProduction[m] >= Demand[m - 1]
         for m in [1]), "DemandSatisfaction_1")
    model.addConstrs(
        (Inventory[m - 1] + RegularTimeProduction[m] +
         OvertimeProduction[m] >= Demand[m - 1]
         for m in range(2, MonthNum + 1)), "DemandSatisfaction_Rest")

    # Constraint 4: Regular time production limit constraint
    model.addConstrs((RegularTimeProduction[m] <= RegularTimeProductionLimit
                      for m in Months), "RegularTimeLimit")

    # Constraint 5: Overtime production limit constraint
    model.addConstrs((OvertimeProduction[m] <= OvertimeProductionLimit
                      for m in Months), "OvertimeLimit")

    # Optimize the model
    model.optimize()

    # Return results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_production_planning()
    print(result)