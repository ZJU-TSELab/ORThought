import gurobipy as gp
from gurobipy import GRB


def solve_forklift_leasing(
    demand=[6, 9, 12, 8, 5, 7, 4],
    long_term_cost=240,
    short_term_cost=390,
    shared_cost=220,
    shared_weeks=[2, 4, 5],
    promo_cost=190,
    promo_max_num=2,
    promo_weeks=[4, 5, 6, 7]):
    """
    Models and solves the forklift leasing optimization problem.
    """
    # --- 1. Model Creation ---
    model = gp.Model("ForkliftLeasing")

    # --- 2. Parameters & Sets ---
    week_num = len(demand)
    weeks = range(1, week_num + 1)
    long_term_weeks = week_num

    # --- 3. Decision Variables ---
    long_term_num = model.addVar(vtype=GRB.INTEGER, name="LongTermNum")
    short_term_num = model.addVars(weeks, vtype=GRB.INTEGER, name="ShortTermNum")
    shared_num = model.addVar(vtype=GRB.INTEGER, name="SharedNum")
    promo_num = model.addVars(weeks, vtype=GRB.INTEGER, name="PromoNum")

    # --- 4. Objective Function ---
    objective = long_term_cost * long_term_num * long_term_weeks
    objective += short_term_cost * gp.quicksum(short_term_num[i] for i in weeks)
    objective += shared_cost * shared_num * len(shared_weeks)
    objective += promo_cost * gp.quicksum(promo_num[i]
                                          for i in weeks if i in promo_weeks)
    model.setObjective(objective, GRB.MINIMIZE)

    # --- 5. Constraints ---
    # Constraint 1: Total forklifts per week must meet demand (non-shared weeks)
    for i in weeks:
        if i not in shared_weeks:
            model.addConstr(long_term_num + short_term_num[i] + promo_num[i]
                            >= demand[i - 1],
                            name=f"Demand_Week_{i}")

    # Constraint 2: Total forklifts during shared weeks must meet demand
    for i in shared_weeks:
        model.addConstr(long_term_num + short_term_num[i] + shared_num +
                        promo_num[i] >= demand[i - 1],
                        name=f"Demand_SharedWeek_{i}")

    # Constraint 3: Promotional forklift quantity must not exceed maximum limit
    for i in promo_weeks:
        model.addConstr(promo_num[i] <= promo_max_num, name=f"PromoLimit_Week_{i}")

    # Constraint 4: Non-promotional weeks cannot lease promotional forklifts
    for i in weeks:
        if i not in promo_weeks:
            model.addConstr(promo_num[i] == 0, name=f"NoPromo_Week_{i}")

    # --- 6. Solve the Model ---
    model.optimize()

    # --- 7. Return Results ---
    if model.status == GRB.OPTIMAL:
        return {"status": "optimal", "obj": model.ObjVal}
    else:
        return {"status": f"{model.status}"}


# Run the solver function
if __name__ == "__main__":
    result = solve_forklift_leasing()
    print(result)
