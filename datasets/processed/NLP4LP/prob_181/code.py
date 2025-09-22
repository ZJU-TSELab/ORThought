def optimize_transportation():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("PatientTransport")

    # Decision variables
    h = m.addVar(vtype=GRB.INTEGER, name="helicopter_trips", lb=0)
    b = m.addVar(vtype=GRB.INTEGER, name="bus_trips", lb=0)

    # Set objective: minimize total transportation time
    m.setObjective(h + 3 * b, GRB.MINIMIZE)

    # Add constraints
    # Patients transported constraint
    m.addConstr(5 * h + 8 * b >= 120, name="patients_min")
    # Trip proportion constraint: h >= (3/7) * b
    m.addConstr(h >= (3/7) * b, name="trip_ratio")
    # Bus trip limit
    m.addConstr(b <= 10, name="bus_limit")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        return m.objVal
    else:
        return None

# Example usage
if __name__ == "__main__":
    min_time = optimize_transportation()
    if min_time is not None:
        print(f"Minimum Total Transportation Time: {min_time}")
    else:
        print("No feasible solution found.")