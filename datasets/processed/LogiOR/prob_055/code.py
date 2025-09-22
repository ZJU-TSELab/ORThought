import gurobipy as gp
from gurobipy import GRB


def solve_logistics_knapsack(
    items=['A', 'B', 'C', 'D', 'E'],
    weights={'A': 400, 'B': 600, 'C': 300, 'D': 500, 'E': 700},
    base_profits={'A': 120, 'B': 180, 'C': 90, 'D': 150, 'E': 210},
    synergy={
        'A': {'A': 0, 'B': 25, 'C': 15, 'D': 0, 'E': -10},
        'B': {'A': 25, 'B': 0, 'C': 30, 'D': 20, 'E': 0},
        'C': {'A': 15, 'B': 30, 'C': 0, 'D': 10, 'E': 5},
        'D': {'A': 0, 'B': 20, 'C': 10, 'D': 0, 'E': 15},
        'E': {'A': -10, 'B': 0, 'C': 5, 'D': 15, 'E': 0}
    },
    truck_capacity=2000
):
    """
    Solves the logistics knapsack problem.
    """
    # Create a new model
    model = gp.Model("Logistics_Knapsack")

    # Create binary decision variables for each item
    x = model.addVars(items, vtype=GRB.BINARY, name="select")

    # Set objective: maximize total profit (base + synergy)
    base_profit = gp.quicksum(base_profits[i] * x[i] for i in items)
    synergy_profit = gp.quicksum(synergy[i][j] * x[i] * x[j] for i in items for j in items if i <= j)
    model.setObjective(base_profit + synergy_profit, GRB.MAXIMIZE)

    # Add weight capacity constraint
    model.addConstr(gp.quicksum(weights[i] * x[i] for i in items) <= truck_capacity, "weight_limit")

    # Optimize model
    model.optimize()

    # Return results
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_logistics_knapsack()
    print(result)
