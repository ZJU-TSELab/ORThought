import gurobipy as gp
from gurobipy import GRB


def solve_farm_production_optimization(
    ProductionCost=[100, 120, 150],
    YieldCapacity=[500, 400, 600],
    WaterUsage=[6, 8, 6],
    FertilizerUsage=[5, 4, 3],
    Demand=[200, 300, 400, 500],
    TransportationCost=[
        [20, 25, 30, 15],
        [22, 26, 32, 18],
        [18, 24, 28, 14]
    ],
    MaxWaterUsageperTon=7,
    MaxFertilizerUsageperTon=4
):
    """
    Models and solves the farm production and distribution optimization problem.
    """
    # Create a new model
    model = gp.Model("Farm Production and Distribution Optimization")

    # Sets
    Farms = range(len(ProductionCost))
    Stores = range(len(Demand))

    # Decision Variables
    AmountProduced = {}
    for f in Farms:
        for s in Stores:
            AmountProduced[f, s] = model.addVar(
                vtype=GRB.CONTINUOUS,
                name=f"AmountProduced_{f+1}_{s+1}"
            )

    # Objective: Minimize total production and transportation costs
    obj = gp.quicksum(
        ProductionCost[f] * AmountProduced[f, s] + TransportationCost[f][s] * AmountProduced[f, s]
        for f in Farms
        for s in Stores
    )
    model.setObjective(obj, GRB.MINIMIZE)

    # Constraint 1: Demand constraint - each store's demand must be met
    for s in Stores:
        model.addConstr(
            gp.quicksum(AmountProduced[f, s] for f in Farms) >= Demand[s],
            f"Demand_{s+1}"
        )

    # Constraint 2: Yield capacity constraint - each farm's production cannot exceed capacity
    for f in Farms:
        model.addConstr(
            gp.quicksum(AmountProduced[f, s] for s in Stores) <= YieldCapacity[f],
            f"YieldCapacity_{f+1}"
        )

    # Constraint 3: Water usage constraint - average water usage cannot exceed maximum
    total_production = gp.quicksum(AmountProduced[f, s] for f in Farms for s in Stores)
    total_water_usage = gp.quicksum(WaterUsage[f] * AmountProduced[f, s] for f in Farms for s in Stores)
    model.addConstr(
        total_water_usage <= MaxWaterUsageperTon * total_production,
        "WaterUsage"
    )

    # Constraint 4: Fertilizer usage constraint - average fertilizer usage cannot exceed maximum
    total_fertilizer_usage = gp.quicksum(FertilizerUsage[f] * AmountProduced[f, s] for f in Farms for s in Stores)
    model.addConstr(
        total_fertilizer_usage <= MaxFertilizerUsageperTon * total_production,
        "FertilizerUsage"
    )

    # Optimize the model
    model.optimize()

    # Return Results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_farm_production_optimization()
    print(result)
