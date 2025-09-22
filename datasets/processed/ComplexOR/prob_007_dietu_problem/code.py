def solve_diet_problem(
    cost=None,
    f_min=None,
    f_max=None,
    n_min=None,
    n_max=None,
    amt=None
):
    from gurobipy import Model, GRB

    # Default data based on provided sample
    if cost is None:
        cost = [2, 3, 1.5]
    if f_min is None:
        f_min = [0, 0, 0]
    if f_max is None:
        f_max = [100, 100, 100]
    if n_min is None:
        n_min = [50, 60]
    if n_max is None:
        n_max = [200, 250]
    if amt is None:
        amt = [[2, 1, 3], [3, 4, 2]]

    num_foods = len(cost)
    num_nutrients = len(amt)

    # Create model
    model = Model("DietProblem")
    model.setParam('OutputFlag', 0)  # Silence Gurobi output

    # Decision variables: amount of each food to buy
    x = model.addVars(
        range(num_foods),
        lb=f_min,
        ub=f_max,
        vtype=GRB.CONTINUOUS,
        name="x"
    )

    # Objective: minimize total cost
    model.setObjective(
        sum(cost[j] * x[j] for j in range(num_foods)),
        GRB.MINIMIZE
    )

    # Nutrient constraints
    for i in range(num_nutrients):
        nutrient_amounts = amt[i]
        total_nutrient = sum(nutrient_amounts[j] * x[j] for j in range(num_foods))
        if i < len(n_min):
            # Nutrient with minimum requirement
            model.addConstr(total_nutrient >= n_min[i], name=f"nutrient_min_{i}")
        if i < len(n_max):
            # Nutrient with maximum requirement
            model.addConstr(total_nutrient <= n_max[i], name=f"nutrient_max_{i}")

    # Optimize the model
    model.optimize()

    # Check feasibility and return optimal value
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
if __name__ == "__main__":
    result = solve_diet_problem()
    if result is not None:
        print(f"Minimum total cost: {result}")
    else:
        print("No feasible solution found.")