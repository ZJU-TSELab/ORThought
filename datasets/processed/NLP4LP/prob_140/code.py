def optimize_transport(fuel_ship=500, fuel_plane=300, containers_required=500, max_plane_trips=10):
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("TransportOptimization")

    # Decision variables
    x_s = m.addVar(vtype=GRB.INTEGER, name="ship_trips", lb=0)
    x_p = m.addVar(vtype=GRB.INTEGER, name="plane_trips", lb=0)

    # Set objective: minimize total fuel consumption
    m.setObjective(fuel_ship * x_s + fuel_plane * x_p, GRB.MINIMIZE)

    # Add constraints
    # Container requirement
    m.addConstr(40 * x_s + 20 * x_p >= containers_required, "containers_min")
    # Plane trips limit
    m.addConstr(x_p <= max_plane_trips, "max_plane_trips")
    # Ship trips at least 50% of total trips
    m.addConstr(x_s >= x_p, "ship_at_least_equal_plane")
    
    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        total_fuel = m.objVal
        return total_fuel
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_fuel = optimize_transport()
    if min_fuel is not None:
        print(f"Minimum Total Fuel Consumption: {min_fuel}")
    else:
        print("No feasible solution found.")