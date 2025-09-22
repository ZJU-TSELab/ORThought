def optimize_crates():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("BananaCratesMaximize")

    # Decision variables
    # x: number of small crates (at least 5)
    # y: number of large crates (at least 0)
    x = m.addVar(name="small_crates", vtype=GRB.INTEGER, lb=5)
    y = m.addVar(name="large_crates", vtype=GRB.INTEGER, lb=0)

    # Set objective: maximize total number of crates
    m.setObjective(x + y, GRB.MAXIMIZE)

    # Add constraints
    # Total bananas used should not exceed 500
    m.addConstr(20 * x + 50 * y <= 500, name="banana_limit")
    # Large crates at least twice small crates
    m.addConstr(y >= 2 * x, name="large_at_least_twice_small")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the total number of crates (objective value)
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_crates = optimize_crates()
    if max_crates is not None:
        print(f"Maximum Total Number of Crates: {max_crates}")
    else:
        print("No feasible solution found.")