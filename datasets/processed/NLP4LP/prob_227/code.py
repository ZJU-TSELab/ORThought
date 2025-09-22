def optimize_pizza_baking():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Pizza_Baking_Minimize_Time")

    # Decision variables
    L = m.addVar(vtype=GRB.INTEGER, name="Large_Pizzas", lb=0)
    M = m.addVar(vtype=GRB.INTEGER, name="Medium_Pizzas", lb=0)

    # Set objective: minimize total baking time
    m.setObjective(12 * L + 8 * M, GRB.MINIMIZE)

    # Add constraints
    m.addConstr(12 * L + 8 * M >= 10000, name="Dough_Constraint")
    m.addConstr(5 * L + 4 * M >= 4400, name="Toppings_Constraint")
    m.addConstr(M >= 200, name="Medium_Demand")
    m.addConstr(L >= 2 * M, name="Large_vs_Medium_Ratio")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the total baking time of the optimal solution
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_baking_time = optimize_pizza_baking()
    if min_baking_time is not None:
        print(f"Minimum Total Baking Time: {min_baking_time} minutes")
    else:
        print("No feasible solution found.")