def optimize_vitamin_mix():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("VitaminMix")

    # Decision variables: number of cups of drinks A and B
    x = m.addVar(name="A", lb=0)
    y = m.addVar(name="B", lb=0)

    # Set the objective: minimize total Vitamin K
    m.setObjective(4 * x + 12 * y, GRB.MINIMIZE)

    # Add constraints
    # Vitamin A constraint
    m.addConstr(8 * x + 15 * y >= 150, name="VitaminA")
    # Vitamin D constraint
    m.addConstr(6 * x + 2 * y >= 300, name="VitaminD")
    # Vitamin E constraint
    m.addConstr(10 * x + 20 * y <= 400, name="VitaminE")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal value of the objective function
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_vitamin_k = optimize_vitamin_mix()
    if min_vitamin_k is not None:
        print(f"Minimum Vitamin K: {min_vitamin_k}")
    else:
        print("No feasible solution found.")