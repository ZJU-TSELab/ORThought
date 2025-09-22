def optimize_desks_drawers():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Desks_and_Drawers")

    # Decision variables: number of desks and drawers
    x = m.addVar(vtype=GRB.INTEGER, name="Desks")
    y = m.addVar(vtype=GRB.INTEGER, name="Drawers")

    # Set the objective: maximize profit
    m.setObjective(100 * x + 90 * y, GRB.MAXIMIZE)

    # Add constraints
    m.addConstr(40 * x + 30 * y <= 4000, "AssemblyTime")
    m.addConstr(20 * x + 10 * y <= 3500, "SandingTime")
    m.addConstr(x >= 0, "NonNegDesks")
    m.addConstr(y >= 0, "NonNegDrawers")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal profit
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_profit = optimize_desks_drawers()
    if max_profit is not None:
        print(f"Maximum Profit: ${max_profit}")
    else:
        print("No feasible solution found.")