def optimize_nutrition(cost_milk=1, cost_vegetables=2, calcium_milk=40, calcium_veg=15,
                       iron_milk=25, iron_veg=30, min_calcium=100, min_iron=50):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("NutritionOptimization")

    # Decision variables: number of glasses of milk and plates of vegetables
    x = model.addVar(name="milk", lb=0)
    y = model.addVar(name="vegetables", lb=0)

    # Set the objective: minimize total cost
    model.setObjective(cost_milk * x + cost_vegetables * y, GRB.MINIMIZE)

    # Add calcium constraint
    model.addConstr(calcium_milk * x + calcium_veg * y >= min_calcium, name="CalciumReq")
    # Add iron constraint
    model.addConstr(iron_milk * x + iron_veg * y >= min_iron, name="IronReq")

    # Optimize the model
    model.optimize()

    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_cost = optimize_nutrition()
    if min_cost is not None:
        print(f"Minimum Cost: {min_cost}")
    else:
        print("No feasible solution found.")