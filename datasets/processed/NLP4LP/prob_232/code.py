def optimize_meals(
    max_food_waste=800,
    max_wrapping_waste=900,
    time_original=10,
    time_experimental=15,
    food_waste_original=20,
    food_waste_experimental=25,
    wrapping_waste_original=45,
    wrapping_waste_experimental=35
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("RestaurantMealOptimization")

    # Decision variables: number of original and experimental meals
    x = model.addVar(vtype=GRB.INTEGER, name="Original")
    y = model.addVar(vtype=GRB.INTEGER, name="Experimental")

    # Set objective: minimize total cooking time
    model.setObjective(
        time_original * x + time_experimental * y,
        GRB.MINIMIZE
    )

    # Add waste constraints
    model.addConstr(
        food_waste_original * x + food_waste_experimental * y <= max_food_waste,
        name="FoodWasteLimit"
    )
    model.addConstr(
        wrapping_waste_original * x + wrapping_waste_experimental * y <= max_wrapping_waste,
        name="WrappingWasteLimit"
    )

    # Set non-negativity constraints (implicit in variable definition)
    # Solve the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal total cooking time
        return model.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_time = optimize_meals()
    if min_time is not None:
        print(f"Minimum Total Cooking Time: {min_time}")
    else:
        print("No feasible solution found.")