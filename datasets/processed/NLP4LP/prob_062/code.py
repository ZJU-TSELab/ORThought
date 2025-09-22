def optimize_vans():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Vans_Optimization")

    # Decision variables: number of regular and hybrid vans
    x = m.addVar(vtype=GRB.INTEGER, name="RegularVans", lb=0)
    y = m.addVar(vtype=GRB.INTEGER, name="HybridVans", lb=0)

    # Set the objective: minimize total vans
    m.setObjective(x + y, GRB.MINIMIZE)

    # Add delivery constraint
    m.addConstr(500 * x + 300 * y >= 20000, name="DeliveryRequirement")

    # Add pollution constraint
    m.addConstr(200 * x + 100 * y <= 7000, name="PollutionLimit")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the optimal total number of vans
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_vans = optimize_vans()
    if min_vans is not None:
        print(f"Minimum Total Number of Vans: {min_vans}")
    else:
        print("No feasible solution found.")