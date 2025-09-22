def optimize_meal_preps(max_calories=2000, protein_smoothie=2, protein_bar=7,
                          calories_smoothie=300, calories_bar=250):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("MealPrepsMaxProtein")

    # Decision variables: number of smoothies (x) and protein bars (y)
    # Since quantities are discrete, define as integer variables
    x = model.addVar(name="smoothies", vtype=GRB.INTEGER, lb=0)
    y = model.addVar(name="bars", vtype=GRB.INTEGER, lb=0)

    # Add the relationship constraint: y = 2x
    model.addConstr(y >= 2 * x, name="relation")

    # Add caloric constraint
    model.addConstr(
        calories_smoothie * x + calories_bar * y <= max_calories,
        name="calorie_limit"
    )

    # Set the objective: maximize total protein
    total_protein = protein_smoothie * x + protein_bar * y
    model.setObjective(total_protein, GRB.MAXIMIZE)

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the maximum total protein
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_protein = optimize_meal_preps()
    if max_protein is not None:
        print(f"Maximum protein intake: {max_protein:.2f} grams")
    else:
        print("No feasible solution found.")