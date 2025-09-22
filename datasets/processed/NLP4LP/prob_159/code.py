def optimize_snacks():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Snack_Suitcases_Maximize")

    # Decision variables
    # x: number of small suitcases
    # y: number of large suitcases
    x = m.addVar(vtype=GRB.INTEGER, name="small_suitcases")
    y = m.addVar(vtype=GRB.INTEGER, name="large_suitcases")

    # Set objective: maximize total snacks
    m.setObjective(50 * x + 80 * y, GRB.MAXIMIZE)

    # Add constraints
    m.addConstr(x - 2 * y >= 0, "preference_constraint")
    m.addConstr(x <= 70, "max_small")
    m.addConstr(y <= 50, "max_large")
    m.addConstr(y >= 15, "min_large")
    m.addConstr(x + y <= 70, "total_limit")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum total snacks
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_snacks = optimize_snacks()
    if max_snacks is not None:
        print(f"Maximum Snacks in Suitcases: {max_snacks}")
    else:
        print("No feasible solution found.")