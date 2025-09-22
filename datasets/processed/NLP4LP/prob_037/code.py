def optimize_teddy_bears():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("TeddyBearProduction")

    # Decision variables: hours factory 1 and factory 2
    x1 = m.addVar(name="Factory1_hours", lb=0)
    x2 = m.addVar(name="Factory2_hours", lb=0)

    # Set the objective: minimize total cost
    m.setObjective(300 * x1 + 600 * x2, GRB.MINIMIZE)

    # Add constraints based on demand
    m.addConstr(5 * x1 + 10 * x2 >= 20, name="BlackDemand")
    m.addConstr(6 * x1 + 10 * x2 >= 5, name="WhiteDemand")
    m.addConstr(3 * x1 >= 15, name="BrownDemand")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_cost = optimize_teddy_bears()
    if min_cost is not None:
        print(f"Minimum Cost of Teddy Bear Production: {min_cost}")
    else:
        print("No feasible solution found.")