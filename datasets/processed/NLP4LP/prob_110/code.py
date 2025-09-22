def optimize_meal(min_calories=3000, min_protein=80):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("MealOptimization")

    # Decision variables: number of ramen and fries packs
    R = model.addVar(name="R", lb=0)
    F = model.addVar(name="F", lb=0)

    # Objective: minimize total sodium intake
    sodium = 100 * R + 75 * F
    model.setObjective(sodium, GRB.MINIMIZE)

    # Nutritional constraints
    model.addConstr(400 * R + 300 * F >= min_calories, name="Calories")
    model.addConstr(20 * R + 10 * F >= min_protein, name="Protein")

    # Proportion constraint: R <= 0.3*(R+F)
    # Simplified to 7 R <= 3 F
    model.addConstr(7 * R <= 3 * F, name="RamenProportion")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the minimal sodium intake
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_sodium = optimize_meal()
    if min_sodium is not None:
        print(f"Minimum Sodium Intake: {min_sodium}")
    else:
        print("No feasible solution found.")