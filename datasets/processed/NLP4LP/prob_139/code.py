def optimize_honey_transport():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("HoneyTransport")

    # Decision variables
    # x: number of small bottles
    # y: number of large bottles
    x = m.addVar(vtype=GRB.INTEGER, name="small_bottles")
    y = m.addVar(vtype=GRB.INTEGER, name="large_bottles")

    # Set objective: maximize total honey
    m.setObjective(5 * x + 20 * y, GRB.MAXIMIZE)

    # Add constraints
    m.addConstr(x <= 300, "max_small_bottles")
    m.addConstr(y <= 100, "max_large_bottles")
    m.addConstr(x >= 2 * y, "small_at_least_twice_large")
    m.addConstr(x + y <= 200, "total_bottles_limit")
    m.addConstr(y >= 50, "min_large_bottles")
    m.addConstr(x >= 0, "non_negative_small")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum total honey transported
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_honey = optimize_honey_transport()
    if max_honey is not None:
        print(f"Maximum Honey Transported: {max_honey}")
    else:
        print("No feasible solution found.")