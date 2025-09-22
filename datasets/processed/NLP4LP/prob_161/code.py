def optimize_transportation():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("ChickenTransport")

    # Decision variables
    x = m.addVar(vtype=GRB.INTEGER, name="bus_trips")
    y = m.addVar(vtype=GRB.INTEGER, name="car_trips")

    # Set objective: minimize total time
    m.setObjective(2 * x + 1.5 * y, GRB.MINIMIZE)

    # Add constraints
    # Capacity constraint
    m.addConstr(100 * x + 40 * y >= 1200, name="capacity")
    # Bus trip limit
    m.addConstr(x <= 10, name="max_bus_trips")
    # Trip ratio constraint (at least 60% by car)
    m.addConstr(y >= 1.5 * x, name="car_ratio")
    # Non-negativity is implicit in variable definition

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total time
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_time = optimize_transportation()
    if min_time is not None:
        print(f"Minimum Total Time: {min_time}")
    else:
        print("No feasible solution found.")