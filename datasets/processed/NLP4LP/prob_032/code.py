def optimize_diet():
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("Jordan_Diet_Optimization")

    # Decision variables: servings of Rice and Kebab
    x = model.addVar(name="Rice", lb=0)
    y = model.addVar(name="Kebab", lb=0)

    # Set objective: minimize total cost
    model.setObjective(3 * x + 2 * y, GRB.MINIMIZE)

    # Add calorie constraint
    model.addConstr(300 * x + 200 * y >= 2200, name="CalorieRequirement")

    # Add protein constraint
    model.addConstr(4.5 * x + 4 * y >= 30, name="ProteinRequirement")

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
    min_cost = optimize_diet()
    if min_cost is not None:
        print(f"Minimum Cost of Diet: {min_cost}")
    else:
        print("No feasible solution found.")