def minimize_vans():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Minimize_Vans")

    # Decision variables
    V = m.addVar(vtype=GRB.INTEGER, name="Vans", lb=0)
    T = m.addVar(vtype=GRB.INTEGER, name="Trucks", lb=0)

    # Set objective: minimize number of vans
    m.setObjective(V, GRB.MINIMIZE)

    # Add constraints
    # Supply constraint
    m.addConstr(50 * V + 100 * T >= 2000, name="Supply")
    # Truck-to-van ratio constraint
    m.addConstr(T <= V, name="Truck_Van_Ratio")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimum number of vans used
        return V.X
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_vans = minimize_vans()
    if min_vans is not None:
        print(f"Minimum number of vans used: {min_vans}")
    else:
        print("No feasible solution found.")