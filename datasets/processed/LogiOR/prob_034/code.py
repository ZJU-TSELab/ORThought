import gurobipy as gp
from gurobipy import GRB


def solve_fuel_production_optimization(
    Inventory=[8000, 12000],
    QualityRating=[12, 6],
    Revenue=[30, 25],
    DemandperMarketingDollar=[8, 15],
    MinQualityRating=[10, 8]
):
    """
    Models and solves the fuel production and marketing optimization problem.
    """
    # Create a new model
    model = gp.Model("Fuel Production and Marketing Optimization")

    # Sets
    Fuels = range(len(Revenue))
    Feedstocks = range(len(Inventory))

    # Decision Variables
    # Amount of fuel f produced from feedstock s
    ProductionAmount = {}
    for f in Fuels:
        for s in Feedstocks:
            ProductionAmount[f, s] = model.addVar(
                vtype=GRB.CONTINUOUS,
                name=f"ProductionAmount_{f+1}_{s+1}"
            )

    # Marketing budget for each fuel
    MarketingBudget = model.addVars(
        Fuels,
        vtype=GRB.CONTINUOUS,
        name="MarketingBudget"
    )

    # Objective: Maximize profit (revenue - marketing costs)
    obj = gp.quicksum(
        Revenue[f] * gp.quicksum(ProductionAmount[f, s] for s in Feedstocks)
        for f in Fuels
    ) - gp.quicksum(MarketingBudget[f] for f in Fuels)

    model.setObjective(obj, GRB.MAXIMIZE)

    # Constraint 1: Inventory constraint
    for s in Feedstocks:
        model.addConstr(
            gp.quicksum(ProductionAmount[f, s] for f in Fuels) <= Inventory[s],
            f"Inventory_{s+1}"
        )

    # Constraint 2: Quality rating constraint
    for f in Fuels:
        model.addConstr(
            gp.quicksum(QualityRating[s] * ProductionAmount[f, s] for s in Feedstocks) >=
            MinQualityRating[f] * gp.quicksum(ProductionAmount[f, s] for s in Feedstocks),
            f"Quality_{f+1}"
        )

    # Constraint 3: Demand constraint
    for f in Fuels:
        model.addConstr(
            DemandperMarketingDollar[f] * MarketingBudget[f] >=
            gp.quicksum(ProductionAmount[f, s] for s in Feedstocks),
            f"Demand_{f+1}"
        )

    # Optimize the model
    model.optimize()

    # Return Results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_fuel_production_optimization()
    print(result)
