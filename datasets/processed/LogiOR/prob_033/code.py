import gurobipy as gp
from gurobipy import GRB


def solve_apple_processing_optimization(
    Inventory=[90000, 110000],
    Revenue=[0.35, 1.10],
    VariableCost=[0.12, 0.80],
    AverageGrade=[5, 6],
    MaxProcessingCapacity=150000,
    MinPackagePercentage=0.20,
    Grades=[7, 4]
):
    # Create a new model
    model = gp.Model("Apple Processing Optimization")

    # Sets
    Products = range(len(Revenue))

    # Profit per unit for each product
    Profit = [Revenue[p] - VariableCost[p] for p in Products]

    # Create decision variables dictionary
    ProcessedAmount = {}
    for p in Products:
        for g_idx, g in enumerate(Grades):
            ProcessedAmount[p, g_idx] = model.addVar(
                vtype=GRB.CONTINUOUS,
                name=f"ProcessedAmount_{p+1}_{g}"
            )

    # Objective: Maximize profit
    obj = gp.quicksum(
        Profit[p] * ProcessedAmount[p, g_idx]
        for p in Products
        for g_idx in range(len(Grades))
    )
    model.setObjective(obj, GRB.MAXIMIZE)

    # Constraint 1: Inventory constraint
    for g_idx in range(len(Grades)):
        model.addConstr(
            gp.quicksum(ProcessedAmount[p, g_idx] for p in Products) <= Inventory[g_idx],
            f"Inventory_{Grades[g_idx]}"
        )

    # Constraint 2: Average grade constraint
    for p in Products:
        model.addConstr(
            AverageGrade[p] * gp.quicksum(ProcessedAmount[p, g_idx] for g_idx in range(len(Grades))) <=
            gp.quicksum(Grades[g_idx] * ProcessedAmount[p, g_idx] for g_idx in range(len(Grades))),
            f"AverageGrade_{p+1}"
        )

    # Constraint 3: Processing capacity constraint
    model.addConstr(
        gp.quicksum(ProcessedAmount[p, g_idx] for p in Products for g_idx in range(len(Grades))) <= MaxProcessingCapacity,
        "ProcessingCapacity"
    )

    # Constraint 4: Marketing constraint
    model.addConstr(
        gp.quicksum(ProcessedAmount[0, g_idx] for g_idx in range(len(Grades))) >=
        MinPackagePercentage * gp.quicksum(ProcessedAmount[p, g_idx]
                                           for p in Products
                                           for g_idx in range(len(Grades))),
        "Marketing"
    )

    # Optimize the model
    model.optimize()

    # Return results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.objVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_apple_processing_optimization()
    print(result)