def optimize_rides():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Employee_Rides_Optimization")
    
    # Decision variables
    T = m.addVar(name="Taxi_Rides", vtype=GRB.INTEGER, lb=0)
    C = m.addVar(name="Company_Car_Rides", vtype=GRB.INTEGER, lb=30)
    
    # Set objective: minimize taxi rides
    m.setObjective(T, GRB.MINIMIZE)
    
    # Add constraints
    # Employee transportation constraint
    m.addConstr(2 * T + 3 * C >= 500, name="EmployeeTransport")
    
    # Ratio constraint: T >= (2/3) * C
    m.addConstr(T >= (2/3) * C, name="CarRideRatio")
    
    # C >= 30 is already enforced by lb=30
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal number of taxi rides
        return T.X
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_taxi_rides = optimize_rides()
    if min_taxi_rides is not None:
        print(f"Minimum number of taxi rides: {min_taxi_rides}")
    else:
        print("No feasible solution found.")