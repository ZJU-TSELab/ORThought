def optimize_water_transport():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Water_Transport_Maximize")

    # Decision variables
    # x: number of small kegs
    # y: number of large kegs
    x = m.addVar(vtype=GRB.INTEGER, name="small_kegs")
    y = m.addVar(vtype=GRB.INTEGER, name="large_kegs")

    # Set objective: maximize total liters of water transported
    m.setObjective(40 * x + 100 * y, GRB.MAXIMIZE)

    # Add constraints
    m.addConstr(x <= 30, "max_small_kegs")
    m.addConstr(y <= 10, "max_large_kegs")
    m.addConstr(x >= 2 * y, "small_at_least_twice_large")
    m.addConstr(x + y <= 25, "total_kegs_limit")
    m.addConstr(y >= 5, "min_large_kegs")
    m.addConstr(x >= 0, "non_negative_small")
    m.addConstr(y >= 0, "non_negative_large")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the maximum total water transported
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    max_water = optimize_water_transport()
    if max_water is not None:
        print(f"Maximum Total Water Transported: {max_water} liters")
    else:
        print("No feasible solution found.")