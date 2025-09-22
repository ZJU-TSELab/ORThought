def optimize_diet(
    calorie_req=2200,
    protein_req=50,
    carbs_req=70,
    cost_hamburger=6.5,
    cost_wrap=4,
    calories_hamburger=800,
    calories_wrap=450,
    protein_hamburger=19,
    protein_wrap=12,
    carbs_hamburger=20,
    carbs_wrap=10
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("DietOptimization")

    # Decision variables: number of hamburgers and wraps
    x = model.addVar(name="Hamburgers", lb=0)
    y = model.addVar(name="Wraps", lb=0)

    # Set the objective: minimize total cost
    model.setObjective(cost_hamburger * x + cost_wrap * y, GRB.MINIMIZE)

    # Add constraints
    # Calorie constraint
    model.addConstr(calories_hamburger * x + calories_wrap * y >= calorie_req, name="Calories")
    # Protein constraint
    model.addConstr(protein_hamburger * x + protein_wrap * y >= protein_req, name="Protein")
    # Carbohydrate constraint
    model.addConstr(carbs_hamburger * x + carbs_wrap * y >= carbs_req, name="Carbohydrates")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the minimum cost
        return model.objVal
    else:
        # No feasible solution
        return None

# Example usage
if __name__ == "__main__":
    min_cost = optimize_diet()
    if min_cost is not None:
        print(f"Minimum Cost: {min_cost}")
    else:
        print("No feasible solution found.")