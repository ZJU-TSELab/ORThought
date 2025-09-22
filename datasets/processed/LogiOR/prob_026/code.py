import gurobipy as gp
from gurobipy import GRB


def solve_textile_manufacturing(
    ProducedFrom={
        "cotton_fabric": ["cotton", "jute"],
        "linen_fabric": ["linen", "jute", "cotton"],
        "jute_fabric": ["jute", "linen"]
    },
    ReducedFiberRatio={
        "cotton_fabric": 0.7,
        "jute_fabric": 0.75,
        "linen_fabric": 0.8
    },
    PurchasingCost={
        "cotton": 350,
        "jute": 400,
        "linen": 300
    },
    ProcessingCost={
        "cotton": 100,
        "jute": 80,
        "linen": 150
    },
    Availability={
        "cotton": 1000,
        "jute": 800,
        "linen": 600
    },
    Demand={
        "cotton_fabric": 300,
        "jute_fabric": 400,
        "linen_fabric": 200
    }):
    """
    Solves the textile manufacturing optimization problem.
    """
    # Create a new model
    model = gp.Model("Textile Manufacturing Optimization")

    # Sets
    RawMaterials = list(PurchasingCost.keys())
    Products = list(Demand.keys())

    # Decision variables
    X = model.addVars(RawMaterials, Products, vtype=GRB.CONTINUOUS, name="X")

    # Objective: Minimize total cost
    obj = gp.quicksum(
        (PurchasingCost[r] + ProcessingCost[r]) * X[r, p] for p in Products
        for r in RawMaterials if r in ProducedFrom.get(p, []))
    model.setObjective(obj, GRB.MINIMIZE)

    # Constraint 1: Demand constraint
    for p in Products:
        model.addConstr(
            gp.quicksum(ReducedFiberRatio[p] * X[r, p]
                        for r in ProducedFrom[p]) >= Demand[p], f"Demand_{p}")

    # Constraint 2: Availability constraint
    for r in RawMaterials:
        model.addConstr(
            gp.quicksum(X[r, p] for p in Products
                        if r in ProducedFrom.get(p, [])) <= Availability[r],
            f"Availability_{r}")

    # Optimize the model
    model.optimize()

    # Return results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_textile_manufacturing()
    print(result)