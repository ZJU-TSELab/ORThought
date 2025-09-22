import gurobipy as gp
from gurobipy import GRB


def solve_brewery_optimization(
    ProductionCapacity=[200, 300],
    ShippingCapacity=[400, 400],
    ProfitPerThousandGallons=[[500, 450], [480, 520]],
    ExpansionCost=[1000, 1500]
):
    """
    Models and solves the brewery production and distribution optimization problem.
    """
    # Create a new model
    model = gp.Model("Brewery_Production_Distribution_Optimization")

    # Sets
    B = range(len(ProductionCapacity))  # Breweries
    H = range(len(ShippingCapacity))  # Destination Hubs
    Y = range(3)  # Years

    # Decision Variables
    ProductionCapacityAdded = model.addVars(B, lb=0.0, name="ProductionCapacityAdded")
    ProductionFromBrewery2Hub = model.addVars(B, H, Y, lb=0.0, name="ProductionFromBrewery2Hub")

    # Objective Function: Maximize total profit
    profit = gp.quicksum(
        ProductionFromBrewery2Hub[b, h, y] * ProfitPerThousandGallons[b][h]
        for b in B for h in H for y in Y
    )
    expansion_costs = gp.quicksum(
        ProductionCapacityAdded[b] * ExpansionCost[b]
        for b in B
    )
    total_profit = profit - expansion_costs

    model.setObjective(total_profit, GRB.MAXIMIZE)

    # Constraints
    # 1. Production capacity constraint
    for b in B:
        for y in Y:
            model.addConstr(
                gp.quicksum(ProductionFromBrewery2Hub[b, h, y] for h in H) <=
                ProductionCapacity[b] + ProductionCapacityAdded[b],
                f"ProductionCapacity_B{b + 1}_Y{y + 1}"
            )

    # 2. Shipping capacity constraint
    for h in H:
        for y in Y:
            model.addConstr(
                gp.quicksum(ProductionFromBrewery2Hub[b, h, y] for b in B) <= ShippingCapacity[h],
                f"ShippingCapacity_H{h + 1}_Y{y + 1}"
            )

    # Optimize the model
    model.optimize()

    # Return Results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_brewery_optimization()
    print(result)
