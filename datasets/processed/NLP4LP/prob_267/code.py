def optimize_vehicle_fleet():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("TourismFleetOptimization")
    
    # Decision variables: number of sedans and buses
    x = m.addVar(name="sedans", vtype=GRB.INTEGER, lb=0)
    y = m.addVar(name="buses", vtype=GRB.INTEGER, lb=0)
    
    # Set the objective: minimize total number of vehicles
    m.setObjective(x + y, GRB.MINIMIZE)
    
    # Capacity constraint: at least 4600 tourists
    m.addConstr(50 * x + 250 * y >= 4600, name="capacity")
    
    # Pollution constraint: at most 800 units
    m.addConstr(10 * x + 40 * y <= 800, name="pollution")
    
    # Optimize the model
    m.optimize()
    
    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total number of vehicles
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_vehicles = optimize_vehicle_fleet()
    if min_vehicles is not None:
        print(f"Minimum Total Vehicles (Sedans + Buses): {min_vehicles}")
    else:
        print("No feasible solution found.")