def optimize_pills():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("PillProduction")

    # Decision variables
    D = m.addVar(vtype=GRB.INTEGER, name="DaytimePills", lb=0)
    N = m.addVar(vtype=GRB.INTEGER, name="NighttimePills", lb=200)

    # Set objective: minimize total sleep medicine
    m.setObjective(2 * D + 5 * N, GRB.MINIMIZE)

    # Add constraints
    # Total painkiller units constraint
    m.addConstr(6 * D + 5 * N <= 800, name="PainkillerLimit")
    # Pill proportion constraint
    m.addConstr(3 * D >= 2 * N, name="DaytimeProportion")
    # Minimum nighttime pills
    m.addConstr(N >= 200, name="MinNighttimePills")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total sleep medicine used
        return m.objVal
    else:
        # No feasible solution
        return None

# Example usage
if __name__ == "__main__":
    min_sleep_medicine = optimize_pills()
    if min_sleep_medicine is not None:
        print(f"Minimum Total Sleep Medicine: {min_sleep_medicine}")
    else:
        print("No feasible solution found.")