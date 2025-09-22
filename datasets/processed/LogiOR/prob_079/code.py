import gurobipy as gp
from gurobipy import GRB


def solve_coffee_blending(
    beans=['Ethiopia', 'Colombia'],
    processes=['SO', 'HB'],
    inventory={'Ethiopia': 8000, 'Colombia': 12000},
    cupping_score={'Ethiopia': 92, 'Colombia': 87},
    revenue={'SO': 40, 'HB': 28},
    proc_cost={'SO': 5, 'HB': 8.5},
    quality_threshold={'SO': 90, 'HB': 88},
    roaster_capacity_hb=10000,
    min_production_so=2000
):
    """
    Solves the specialty coffee blending and allocation problem to maximize profit.
    """

    # Create a new model
    model = gp.Model("CoffeeBlending")

    # --- Decision Variables ---
    # x[b, p]: kg of bean 'b' allocated to process 'p'
    x = model.addVars(beans, processes, lb=0, name="allocation")

    # --- Objective Function ---
    # Maximize total profit: (Revenue - Processing Cost) * Quantity
    profit = gp.quicksum((revenue[p] - proc_cost[p]) * x[b, p]
                         for b in beans for p in processes)
    model.setObjective(profit, GRB.MAXIMIZE)

    # --- Constraints ---
    # 1. Inventory limits for each bean type
    model.addConstrs((x.sum(b, '*') <= inventory[b] for b in beans),
                     name="inventory")

    # 2. Quality requirements for each product line (linearized)
    for p in processes:
        model.addConstr(gp.quicksum(
            (cupping_score[b] - quality_threshold[p]) * x[b, p]
            for b in beans) >= 0,
                        name=f"quality_{p}")

    # 3. Operational constraints
    model.addConstr(x.sum('*', 'HB') <= roaster_capacity_hb,
                    name="roaster_capacity")
    model.addConstr(x.sum('*', 'SO') >= min_production_so,
                    name="min_so_production")

    # --- Solve the model ---
    model.optimize()

    # --- Return results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


if __name__ == "__main__":
    result = solve_coffee_blending()
    print(result)