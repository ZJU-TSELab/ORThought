import gurobipy as gp
from gurobipy import GRB
import math


def solve_bakery_distribution(
    BakerySupply=[200, 150, 250, 180],
    StoreDemand=[120, 100, 130, 90, 80],
    ShippingDistance=[[10, 15, 20, 25, 30], [12, 8, 18, 22, 28],
                      [14, 10, 16, 20, 26], [16, 12, 14, 18, 24]]):
    """
    Solves the bakery distribution (transportation) problem.
    """
    # --- 1. Model Creation ---
    model = gp.Model("Bakery Distribution Optimization")

    # --- 2. Parameters & Sets ---
    BakeryNum = len(BakerySupply)
    StoreNum = len(StoreDemand)
    Bakeries = range(BakeryNum)
    Stores = range(StoreNum)

    # Calculate shipping costs with square roots
    ShippingCost = [[math.sqrt(dist) for dist in row]
                    for row in ShippingDistance]

    # --- 3. Decision Variables ---
    ShipAmount = model.addVars(Bakeries,
                               Stores,
                               vtype=GRB.INTEGER,
                               name="ShipAmount")

    # --- 4. Objective Function ---
    # Minimize total transportation cost
    model.setObjective(
        gp.quicksum(ShippingCost[b][s] * ShipAmount[b, s] for b in Bakeries
                    for s in Stores), GRB.MINIMIZE)

    # --- 5. Constraints ---
    # Constraint 1: Bakery supply constraint
    model.addConstrs(
        (gp.quicksum(ShipAmount[b, s] for s in Stores) <= BakerySupply[b]
         for b in Bakeries),
        name="BakerySupply")

    # Constraint 2: Store demand constraint
    model.addConstrs(
        (gp.quicksum(ShipAmount[b, s] for b in Bakeries) == StoreDemand[s]
         for s in Stores),
        name="StoreDemand")

    # --- 6. Solve the Model ---
    model.optimize()

    # --- 7. Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_bakery_distribution()
    print(result)