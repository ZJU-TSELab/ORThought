def optimize_fertilizer_cost():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Fertilizer_Optimization")

    # Decision variables: amount of fertilizers C and Y
    x = m.addVar(name="C", lb=0)  # fertilizer C in kg
    y = m.addVar(name="Y", lb=0)  # fertilizer Y in kg

    # Set the objective: minimize total cost
    m.setObjective(2 * x + 3 * y, GRB.MINIMIZE)

    # Add constraints
    m.addConstr(1.5 * x + 5 * y >= 5, name="NitrousOxide")
    m.addConstr(3 * x + y >= 8, name="VitaminMix")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_cost = optimize_fertilizer_cost()
    if min_cost is not None:
        print(f"Minimum Cost of Fertilizer Mixture: {min_cost}")
    else:
        print("No feasible solution found.")