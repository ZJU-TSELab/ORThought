def optimize_diet(
    food_set=['Apple', 'Banana'],
    nutrient_set=['VitaminC', 'Fiber'],
    food_cost=[2.0, 1.5],
    min_food_amount=[0, 0],
    max_food_amount=[10, 10],
    min_nutrient_amount=[50, 30],
    max_nutrient_amount=[100, 60],
    nutrient_amount=[[10, 5], [5, 10]]
):
    import gurobipy as gp
    from gurobipy import GRB

    # Number of foods and nutrients
    J = len(food_set)
    I = len(nutrient_set)

    # Create model
    model = gp.Model("DietProblem")
    model.Params.OutputFlag = 0  # Suppress output

    # Decision variables: amount of each food
    x = model.addVars(J, lb=0, ub=0, name='x')  # Initialize with bounds, will set properly below

    # Set bounds for each food variable
    for j in range(J):
        x[j].lb = min_food_amount[j]
        x[j].ub = max_food_amount[j]

    # Objective: minimize total cost
    model.setObjective(
        gp.quicksum(food_cost[j] * x[j] for j in range(J)),
        GRB.MINIMIZE
    )

    # Nutrient constraints
    for i in range(I):
        # Total nutrient in diet
        total_nutrient = gp.quicksum(nutrient_amount[i][j] * x[j] for j in range(J))
        # Lower bound
        model.addConstr(total_nutrient >= min_nutrient_amount[i], name=f"nutrient_{i}_min")
        # Upper bound
        model.addConstr(total_nutrient <= max_nutrient_amount[i], name=f"nutrient_{i}_max")

    # Optimize
    model.optimize()

    # Check feasibility and return result
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
if __name__ == "__main__":  
    result = optimize_diet()
    if result is not None:
        print(f"Minimum total cost: {result}")
    else:
        print("No feasible solution found.")