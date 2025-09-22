def optimize_pills():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Pill_Optimization")

    # Decision variables: number of pills A and B
    x_A = m.addVar(name="x_A", lb=0, vtype=GRB.INTEGER)
    x_B = m.addVar(name="x_B", lb=0, vtype=GRB.INTEGER)

    # Set the objective: minimize total cost
    m.setObjective(4 * x_A + 5 * x_B, GRB.MINIMIZE)

    # Add constraints
    m.addConstr(3 * x_A + 6 * x_B >= 40, name="SleepRequirement")
    m.addConstr(5 * x_A + 1 * x_B >= 50, name="AntiInflammatoryRequirement")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal objective value
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_cost = optimize_pills()
    if min_cost is not None:
        print(f"Minimum Cost of Pills: {min_cost}")
    else:
        print("No feasible solution found.")