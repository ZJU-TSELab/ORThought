def optimize_meal_delivery():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("MealDeliveryOptimization")

    # Decision variables
    x_b = m.addVar(vtype=GRB.INTEGER, name="bikes")
    x_s = m.addVar(vtype=GRB.INTEGER, name="scooters")

    # Set objective: maximize total meals
    m.setObjective(8 * x_b + 5 * x_s, GRB.MAXIMIZE)

    # Add constraints
    # Charge constraint
    m.addConstr(3 * x_b + 2 * x_s <= 200, name="charge_limit")
    # Bike usage limit (30% of total vehicles)
    m.addConstr(7 * x_b <= 3 * x_s, name="bike_ratio")
    # Minimum scooters
    m.addConstr(x_s >= 20, name="min_scooters")
    # Non-negativity is implicit in variable definition

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum number of meals delivered
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_meals = optimize_meal_delivery()
    if max_meals is not None:
        print(f"Maximum Meals Delivered: {max_meals}")
    else:
        print("No feasible solution found.")