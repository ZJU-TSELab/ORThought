def optimize_gift_delivery(
    max_trips_new=15,
    min_gifts=1000,
    gifts_per_trip_new=50,
    gifts_per_trip_old=70,
    diesel_per_trip_new=30,
    diesel_per_trip_old=40,
    min_old_trip_fraction=0.4
):
    import gurobipy as gp
    from gurobipy import GRB

    # Create a new model
    model = gp.Model("GiftDeliveryOptimization")
    
    # Decision variables
    x = model.addVar(vtype=GRB.INTEGER, name="x_trips_new")  # Trips by new company
    y = model.addVar(vtype=GRB.INTEGER, name="y_trips_old")  # Trips by old company
    
    # Set objective: minimize total diesel consumption
    model.setObjective(
        diesel_per_trip_new * x + diesel_per_trip_old * y,
        GRB.MINIMIZE
    )
    
    # Add constraints
    # Delivery requirement
    model.addConstr(
        gifts_per_trip_new * x + gifts_per_trip_old * y >= min_gifts,
        name="DeliveryRequirement"
    )
    # Trips limit for new company
    model.addConstr(
        x <= max_trips_new,
        name="MaxTripsNew"
    )
    # Old company trips proportion constraint: y >= 0.4*(x + y)
    model.addConstr(
        y >= min_old_trip_fraction * (x + y),
        name="OldTripProportion"
    )
    # Non-negativity constraints are implicit in variable types
    
    # Optimize the model
    model.optimize()
    
    # Check if a feasible solution was found
    if model.status == GRB.OPTIMAL:
        # Return the total diesel used in the optimal solution
        return model.objVal
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    total_diesel = optimize_gift_delivery()
    if total_diesel is not None:
        print(f"Minimum Total Diesel Consumption: {total_diesel}")
    else:
        print("No feasible solution found.")