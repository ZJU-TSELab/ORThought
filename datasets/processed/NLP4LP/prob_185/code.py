def minimize_ships():
    from gurobipy import Model, GRB

    # Create a new model
    m = Model("Minimize_Ships")

    # Decision variables: number of large and small ships
    L = m.addVar(vtype=GRB.INTEGER, name="LargeShips", lb=0)
    S = m.addVar(vtype=GRB.INTEGER, name="SmallShips", lb=0)

    # Set the objective: minimize total number of ships
    m.setObjective(L + S, GRB.MINIMIZE)

    # Add capacity constraint
    m.addConstr(500 * L + 200 * S >= 3000, name="CapacityConstraint")

    # Add port constraint: large ships cannot exceed small ships
    m.addConstr(L <= S, name="PortConstraint")

    # Optimize the model
    m.optimize()

    # Check if a feasible solution was found
    if m.status == GRB.OPTIMAL:
        # Return the minimum total number of ships
        return m.objVal
    else:
        # No feasible solution
        return None
# Example usage
if __name__ == "__main__":
    min_ships = minimize_ships()
    if min_ships is not None:
        print(f"Minimum Total Ships (Large + Small): {min_ships}")
    else:
        print("No feasible solution found.")