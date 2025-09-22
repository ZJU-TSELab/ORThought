import gurobipy as gp
from gurobipy import GRB


def solve_product_manufacturing_optimization(
    ProductPerRawMaterial=[2, 3, 2, 3],
    LaborHoursPerRawMaterial=2,
    LaborHoursPerProduct=[0, 0, 3, 4],
    SellingPrice=[10, 12, 20, 25],
    ProcessingCost=[0, 0, 5, 6],
    RawMaterialCost=5,
    MaxLaborHours=8000,
    MaxRawMaterial=3000
):
    """
    Models and solves the product manufacturing optimization problem.
    """
    # Create a new model
    model = gp.Model("Product Manufacturing Optimization")

    # Sets
    Products = range(len(SellingPrice))

    # Decision Variables
    RawMaterialPurchased = model.addVar(vtype=GRB.INTEGER, name="RawMaterialPurchased")
    ProductProduced = model.addVars(Products, vtype=GRB.INTEGER, name="ProductProduced")

    # Objective: Maximize profit
    revenue = gp.quicksum(SellingPrice[p] * ProductProduced[p] for p in Products)
    raw_material_cost = RawMaterialCost * RawMaterialPurchased
    processing_cost = gp.quicksum(ProcessingCost[p] * ProductProduced[p] for p in Products)

    model.setObjective(revenue - raw_material_cost - processing_cost, GRB.MAXIMIZE)

    # Constraint 1: Labor hours constraint
    labor_hours = (LaborHoursPerRawMaterial * RawMaterialPurchased +
                   gp.quicksum(LaborHoursPerProduct[p] * ProductProduced[p] for p in Products))
    model.addConstr(labor_hours <= MaxLaborHours, "LaborHours")

    # Constraint 2: Raw material constraint
    model.addConstr(RawMaterialPurchased <= MaxRawMaterial, "RawMaterial")

    # Constraint 3: Product production constraint
    model.addConstr(
        gp.quicksum(ProductProduced[p] for p in Products) ==
        gp.quicksum(ProductPerRawMaterial[p] * RawMaterialPurchased for p in Products),
        "ProductionBalance"
    )

    # Optimize the model
    model.optimize()

    # Return Results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_product_manufacturing_optimization()
    print(result)
