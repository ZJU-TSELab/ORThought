def optimize_food_servings():
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("FoodOptimization")

    # Decision variables: servings of vegetables and fruits
    x = model.addVar(name="vegetables", lb=0)
    y = model.addVar(name="fruits", lb=0)

    # Set the objective: minimize total cost
    model.setObjective(3 * x + 5 * y, GRB.MINIMIZE)

    # Add constraints
    # Vitamins constraint
    model.addConstr(2 * x + 4 * y >= 20, name="Vitamins")
    # Minerals constraint
    model.addConstr(3 * x + y >= 30, name="Minerals")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the optimal cost
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_cost = optimize_food_servings()
    if min_cost is not None:
        print(f"Minimum Cost of Food Servings: {min_cost}")
    else:
        print("No feasible solution found.")