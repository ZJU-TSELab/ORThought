def optimize_transportation():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Employee_Transport_MinPollution")

    # Decision variables
    # Number of cars
    x = m.addVar(vtype=GRB.INTEGER, name="cars", lb=0)
    # Number of buses
    y = m.addVar(vtype=GRB.INTEGER, name="buses", lb=0, ub=4)

    # Set objective: minimize total pollution
    m.setObjective(10 * x + 30 * y, GRB.MINIMIZE)

    # Add constraints
    # Ensure at least 300 employees are transported
    m.addConstr(4 * x + 20 * y >= 300, "transport_capacity")
    # Limit on number of buses
    m.addConstr(y <= 4, "bus_limit")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total pollution
        return m.objVal
    else:
        # No feasible solution
        return None

# Example usage
if __name__ == "__main__":
    min_pollution = optimize_transportation()
    if min_pollution is not None:
        print(f"Minimum Total Pollution: {min_pollution}")
    else:
        print("No feasible solution found.")