def optimize_monkey_transport():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("MonkeyTransport")

    # Decision variables
    x_b = m.addVar(vtype=GRB.INTEGER, name="bus_trips")
    x_c = m.addVar(vtype=GRB.INTEGER, name="car_trips")

    # Set objective: minimize total time
    m.setObjective(30 * x_b + 15 * x_c, GRB.MINIMIZE)

    # Add constraints
    # Capacity constraint
    m.addConstr(20 * x_b + 6 * x_c >= 300, name="capacity")
    # Bus trip limit
    m.addConstr(x_b <= 10, name="max_bus_trips")
    # Proportion constraint (2 * x_c >= 3 * x_b)
    m.addConstr(2 * x_c >= 3 * x_b, name="car_ratio")
    # Non-negativity is implicit in variable definition

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimal total time
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_time = optimize_monkey_transport()
    if min_time is not None:
        print(f"Minimum Total Time: {min_time}")
    else:
        print("No feasible solution found.")