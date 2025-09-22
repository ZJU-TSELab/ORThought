def optimize_feed_mixture():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Feed_Mixture_Min_Cost")

    # Decision variables: amount of Feed A and Feed B
    x = m.addVar(name="Feed_A", lb=0)
    y = m.addVar(name="Feed_B", lb=0)

    # Set the objective: minimize total cost
    m.setObjective(100 * x + 80 * y, GRB.MINIMIZE)

    # Add protein constraint
    m.addConstr(10 * x + 7 * y >= 30, name="ProteinConstraint")

    # Add fat constraint
    m.addConstr(8 * x + 15 * y >= 50, name="FatConstraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal cost
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_cost = optimize_feed_mixture()
    if min_cost is not None:
        print(f"Minimum Cost of Feed Mixture: {min_cost}")
    else:
        print("No feasible solution found.")