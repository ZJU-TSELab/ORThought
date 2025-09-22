import gurobipy as gp
from gurobipy import GRB


def solve_logistics_optimization(
    parcels=[1, 2, 3, 4, 5, 6, 7, 8],
    trucks=[1, 2, 3],
    weights={1: 35, 2: 45, 3: 25, 4: 50, 5: 30, 6: 40, 7: 20, 8: 55},
    base_revenues={
        1: 50,
        2: 75,
        3: 40,
        4: 80,
        5: 60,
        6: 65,
        7: 35,
        8: 90
    },
    capacities={1: 100, 2: 120, 3: 80},
    synergy_bonuses={
        (1, 3): 25,
        (2, 5): 30,
        (2, 6): 20,
        (4, 8): 40,
        (5, 7): 22
    }
):
    """
    Models and solves the quadratic multiple knapsack problem for RapidLink Logistics
    """
    # --- 1. Model Creation ---
    model = gp.Model("QuadraticKnapsackLogistics")

    # --- 2. Decision Variables ---
    # x[i, j] = 1 if parcel i is assigned to truck j, 0 otherwise.
    x = model.addVars(parcels, trucks, vtype=GRB.BINARY, name="assign")

    # --- 3. Objective Function ---
    # The total revenue is the sum of base revenues plus synergy bonuses.
    synergy_revenue = gp.quicksum(synergy_bonuses[i, k] * x[i, j] * x[k, j]
                                    for (i, k) in synergy_bonuses
                                    for j in trucks)
    sum_base_revenue = gp.quicksum(base_revenues[i] for i in parcels)

    model.setObjective(synergy_revenue + sum_base_revenue, GRB.MAXIMIZE)

    # --- 4. Constraints ---

    # Constraint 1: Each parcel must be assigned to exactly one truck.
    for i in parcels:
        model.addConstr(gp.quicksum(x[i, j] for j in trucks) == 1,
                        name=f"parcel_assign_{i}")

    # Constraint 2: The weight in each truck cannot exceed its capacity.
    for j in trucks:
        model.addConstr(gp.quicksum(weights[i] * x[i, j] for i in parcels)
                        <= capacities[j],
                        name=f"truck_capacity_{j}")

    # --- 5. Solve the Model ---
    model.optimize()

    # --- 6. Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == "__main__":
    result = solve_logistics_optimization()
    print(result)
