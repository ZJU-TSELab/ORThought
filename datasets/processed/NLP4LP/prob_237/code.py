def optimize_meals():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("MealOptimization")

    # Decision variables: number of salads (x) and fruit bowls (y)
    # Assuming integer quantities for practical purposes
    x = m.addVar(name="Salads", lb=0, vtype=GRB.INTEGER)
    y = m.addVar(name="FruitBowls", lb=0, vtype=GRB.INTEGER)

    # Set the objective: maximize potassium intake
    m.setObjective(2 * x + 8 * y, GRB.MAXIMIZE)

    # Add constraints
    # Vitamin constraint
    m.addConstr(7 * x + 15 * y >= 90, name="Vitamin")
    # Fibre constraint
    m.addConstr(12 * x + 3 * y >= 110, name="Fibre")
    # Fruit bowl proportion constraint
    m.addConstr(y <= (3/7) * x, name="FruitProportion")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum potassium intake
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_potassium = optimize_meals()
    if max_potassium is not None:
        print(f"Maximum Potassium Intake: {max_potassium} mg")
    else:
        print("No feasible solution found.")