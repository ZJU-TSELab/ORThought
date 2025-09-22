def optimize_vehicle_allocation():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Vehicle_Optimization")

    # Decision variables: number of limousines and buses
    L = m.addVar(vtype=GRB.INTEGER, name="Limousines", lb=0)
    B = m.addVar(vtype=GRB.INTEGER, name="Buses", lb=0)

    # Set the objective: minimize total number of vehicles
    m.setObjective(L + B, GRB.MINIMIZE)

    # Add capacity constraint
    m.addConstr(12 * L + 18 * B >= 400, name="CapacityConstraint")

    # Add ratio constraint: 3L >= 7B
    m.addConstr(3 * L >= 7 * B, name="RatioConstraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        total_vehicles = L.X + B.X
        return total_vehicles
    else:
        return None
# Example usage
if __name__ == "__main__":
    min_vehicles = optimize_vehicle_allocation()
    if min_vehicles is not None:
        print(f"Minimum Total Vehicles: {min_vehicles}")
    else:
        print("No feasible solution found.")