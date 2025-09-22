def optimize_vehicle_allocation():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("VoterTransport")

    # Decision variables
    V = m.addVar(vtype=GRB.INTEGER, name="Vans")
    C = m.addVar(vtype=GRB.INTEGER, name="Cars")

    # Set objective: minimize number of cars
    m.setObjective(C, GRB.MINIMIZE)

    # Capacity constraint: total capacity ≥ 200 voters
    m.addConstr(6 * V + 3 * C >= 200, name="Capacity")

    # Vehicle ratio constraint: vans ≤ 30% of total vehicles
    # Derived as: 7V ≤ 3C
    m.addConstr(7 * V <= 3 * C, name="Vans_ratio")

    # Non-negativity constraints are implicit in variable definitions

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimal number of cars used
        return C.X
    else:
        # No feasible solution found
        return None
# Example usage
if __name__ == "__main__":
    min_cars = optimize_vehicle_allocation()
    if min_cars is not None:
        print(f"Minimum number of cars needed: {min_cars}")
    else:
        print("No feasible solution found.")