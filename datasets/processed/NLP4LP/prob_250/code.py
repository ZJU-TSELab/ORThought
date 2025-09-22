def optimize_taxi_fleet():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("TaxiFleetOptimization")

    # Decision variables
    x = m.addVar(vtype=GRB.INTEGER, name="motorcycles", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="sedans", lb=0)

    # Set objective: maximize total earnings
    m.setObjective(100 * x + 225 * y, GRB.MAXIMIZE)

    # Add constraints
    # Capacity constraint
    m.addConstr(30 * x + 70 * y >= 1200, name="capacity")
    # Motorcycle proportion constraint
    m.addConstr(4 * x <= y, name="motorcycle_ratio")
    # Pollution constraint
    m.addConstr(4 * x + 15 * y <= 200, name="pollution")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal objective value
        return m.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    max_earnings = optimize_taxi_fleet()
    if max_earnings is not None:
        print(f"Maximum Total Earnings: ${max_earnings}")
    else:
        print("No feasible solution found.")