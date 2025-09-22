def optimize_butcher_shops():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("HotDogShopOptimization")

    # Decision variables: number of small and large shops
    # Both are integers and non-negative
    x = m.addVar(vtype=GRB.INTEGER, name="small_shops", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="large_shops", lb=0)

    # Set the objective: minimize total number of shops
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add production constraint: at least 500 hot dogs
    m.addConstr(30 * x + 70 * y >= 500, name="production_constraint")

    # Add labor constraint: no more than 30 workers
    m.addConstr(2 * x + 4 * y <= 30, name="labor_constraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal objective value (minimum total shops)
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_shops = optimize_butcher_shops()
    if min_shops is not None:
        print(f"Minimum Total Number of Shops: {min_shops}")
    else:
        print("No feasible solution found.")