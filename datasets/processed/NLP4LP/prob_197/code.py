def optimize_supplements():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("SupplementsOptimization")

    # Decision variables: servings of supplement A and B
    x = m.addVar(name="A_servings", lb=0)
    y = m.addVar(name="B_servings", lb=0)

    # Set the objective: minimize total cost
    m.setObjective(14 * x + 25 * y, GRB.MINIMIZE)

    # Add constraints
    # Calcium constraint
    m.addConstr(30 * x + 60 * y >= 400, name="CalciumRequirement")
    # Magnesium constraint
    m.addConstr(50 * x + 10 * y >= 50, name="MagnesiumRequirement")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal cost
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_cost = optimize_supplements()
    if min_cost is not None:
        print(f"Minimum Cost: {min_cost}")
    else:
        print("No feasible solution found.")