def optimize_stores():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Minimize_Stores")

    # Decision variables: number of retail and outlet stores
    R = m.addVar(vtype=GRB.INTEGER, name="RetailStores", lb=0)
    F = m.addVar(vtype=GRB.INTEGER, name="OutletStores", lb=0)

    # Set the objective: minimize total number of stores
    m.setObjective(R + F, GRB.MINIMIZE)

    # Add customer constraint
    m.addConstr(200 * R + 80 * F >= 1200, name="CustomerCoverage")

    # Add staffing constraint
    m.addConstr(6 * R + 4 * F <= 50, name="StaffingLimit")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total number of stores
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_stores = optimize_stores()
    if min_stores is not None:
        print(f"Minimum Total Stores (Retail + Outlet): {min_stores}")
    else:
        print("No feasible solution found.")