def optimize_shipment():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Meat_Shipment")

    # Decision variables: number of truck trips and van trips
    T = m.addVar(vtype=GRB.INTEGER, name="TruckTrips", lb=0)
    V = m.addVar(vtype=GRB.INTEGER, name="VanTrips", lb=0)

    # Set the objective: minimize total trips
    m.setObjective(T + V, GRB.MINIMIZE)

    # Capacity constraint: at least 50,000 patties shipped
    m.addConstr(1000 * T + 500 * V >= 50000, name="DemandConstraint")

    # Budget constraint: total cost not exceeding $12,500
    m.addConstr(300 * T + 100 * V <= 12500, name="BudgetConstraint")

    # Vehicle count constraint: trucks not more than vans
    m.addConstr(T <= V, name="VehicleCountConstraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimal total number of trips
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_trips = optimize_shipment()
    if min_trips is not None:
        print(f"Minimum Total Trips (Trucks + Vans): {min_trips}")
    else:
        print("No feasible solution found.")