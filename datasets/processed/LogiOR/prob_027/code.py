import gurobipy as gp
from gurobipy import GRB


def solve_product_distribution(
    HubInventoryRequirement=300,
    StoreStandardProducts=[150, 250, 300],
    StorePremiumProducts=[30, 100, 70],
    ShippingDistance=[[0, 12, 18], [12, 0, 15], [18, 15, 0]]):
    """
    Solves the product distribution optimization problem.
    """
    # Create a new model
    model = gp.Model("Product Distribution Optimization")

    # Parameters and Sets
    DistributionCenterNum = len(StoreStandardProducts)
    FulfillmentHubNum = len(ShippingDistance)
    ProductTypeNum = 2  # 0 for standard, 1 for premium

    DCs = range(DistributionCenterNum)
    Hubs = range(FulfillmentHubNum)
    Products = range(ProductTypeNum)

    # Decision Variables
    ShipAmount = model.addVars(DCs,
                               Hubs,
                               Products,
                               vtype=GRB.INTEGER,
                               name="ShipAmount")

    # Objective: Minimize total transportation distance
    model.setObjective(
        gp.quicksum(ShippingDistance[d][h] * ShipAmount[d, h, p]
                    for d in DCs for h in Hubs for p in Products),
        GRB.MINIMIZE)

    # Constraint 1: Fulfillment hub inventory constraint
    model.addConstrs(
        (gp.quicksum(ShipAmount[d, h, p] for d in DCs for p in Products) ==
         HubInventoryRequirement for h in Hubs),
        name="Hub_Inventory")

    # Constraint 2: Product type balance constraint (standard products)
    # This constraint limits the amount shipped on each individual path
    # based on the total stock at the distribution center.
    model.addConstrs(
        (ShipAmount[d, h, 0] <= StoreStandardProducts[d] for d in DCs
         for h in Hubs),
        name="Standard_Product_Limit")

    # Constraint 3: Product type balance constraint (premium products)
    model.addConstrs(
        (ShipAmount[d, h, 1] <= StorePremiumProducts[d] for d in DCs
         for h in Hubs),
        name="Premium_Product_Limit")

    # Optimize the model
    model.optimize()

    # Return results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_product_distribution()
    print(result)